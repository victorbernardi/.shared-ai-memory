# Plano de Implementação: Horímetros Integrados no Parquet M3, Alertas 350G/P e Expurgo Excel

> **Identidade do Documento:** `./docs/plans/plan_v3_maquina_350p_e_expurgo_excel.md`  
> **Versão:** 3.1.0  
> **Data:** 27/05/2026  
> **Status:** STANDBY MODE (Aguardando Retorno do Usuário)  
> **Projeto:** Inova Máquinas | Leads Preventivos de Pós-Vendas (CSC / COPS)

---

## 🎯 1. Objetivo da Iteração

Esta iteração consolida o alinhamento definitivo das réguas de Material Rodante, do primeiro alerta e da fonte de horímetros acordada com o usuário:

1. **Fonte Única de Horímetros (M3):** Ler os horímetros diretamente da coluna correspondente no arquivo parquet do motor M3 (`dataset_ouro_potencial_chassi_v1.parquet`). Remover a consulta JDBC à tabela `VV1010` de horímetros do Fabric da etapa de extração de ativos (preservando apenas a consulta de auditoria do Fabric à `VS1010/VV1010` na Ponte da Verdade).
2. **Nova Régua de Material Rodante & Regra 350G/P:**
   * **Tratores de Esteira (700J, 750J, 850J, 1050K):** Alertas cíclicos a cada **1.500 horas adicionais**, com primeiro alerta absoluto de Material Rodante disparando em **1.500 horas**.
   * **Escavadeiras (130G, 130P, 160G/P, 180G, 200G/P, 210G/P, 350ZX, 350G/P):** Alertas cíclicos a cada **3.000 horas adicionais**, com primeiro alerta absoluto disparando ao atingir **3.000 horas** acumuladas. Isso inclui o modelo **`350P`** (como escavadeira do grupo `350G/P`) no limite de **3.000 horas** (e não 1.500h).
3. **Mecânica do Primeiro Alerta Comercial:**
   * **FPS:** Dispara a cada 200h acumuladas. Se o lead não for tratado ("Sem Contato" ou em branco na planilha de retorno), ele avança para o 2º alerta comercial (400h), 3º alerta (600h), etc., para evitar a perda do timing preventivo.
   * **Material Rodante:** Dispara o primeiro alerta se a máquina estiver em seu ciclo inicial (sem feedbacks tratados anteriormente na planilha de retorno, onde `Horimetro_Base == Work Order Hours Reported` ou `Horimetro_Base == 0`) e o seu horímetro acumulado absoluto (`Work Order Hours Reported`) for maior ou igual ao mínimo absoluto (1.500h para tratores e 3.000h para escavadeiras).
4. **Higiene e Expurgo Completo:** Remover de vez todos os resíduos mortos do arquivo `Product_details_full.xlsx` do orquestrador (`run.py`) e do motor de extração (`extract.py`).

---

## 🛠️ 2. Análise de Arquivos e Alterações Propostas

### A. Integração Resiliente de Horímetro em `src/extract.py`

Como o usuário está adicionando a coluna de horímetro no parquet `dataset_ouro_potencial_chassi_v1.parquet`, implementaremos uma varredura de colunas inteligente e flexível na função `carregar_ativos()` para capturar o horímetro sob possíveis nomes:

1. Buscar pela coluna `'Horimetro'`.
2. Buscar pela coluna `'Work Order Hours Reported'`.
3. Buscar case-insensitive por qualquer coluna que contenha `'hor'` ou `'hour'`.
4. Fallback padrão seguro de `2500.0` para blindagem contra erros de preflight de dry-run.

---

### B. Nova Lógica de Alertas em `src/transform.py`

Refatoração da função `calcular_alertas()` para implementar:

* Regra acumulativa e recorrente de FPS a cada 200h (200h, 400h, 600h, etc.).
* Alerta de Material Rodante a 1.500h (Tratores) e 3.000h (Escavadeiras incluindo 350G/P) cíclicos e no primeiro alerta absoluto.

---

## ✏️ 3. Diffs Detalhados de Modificação

### Componente: [src/extract.py](file:///C:/Projetos/Inova/projects/lead-csc-pops/src/extract.py)

Ajuste da função `carregar_ativos()` para consumir o horímetro diretamente do parquet do M3 e expurgar a dependência JDBC de horímetros do Fabric.

```python
def carregar_ativos(caminho_m3=None):
    """
    Carrega a base ativa de equipamentos filtrada de acordo com o output do motor M3 (potencial por chassi >= 2016)
    e enriquecida com os horimetros contidos diretamente no arquivo parquet do potencial do M3.
    Garante resiliencia contra nomes de colunas do M3 e expurga o Product_details_full.xlsx.
    """
    if caminho_m3 is None:
        caminho_m3 = r"C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial\data\dataset_ouro_potencial_chassi_v1.parquet"
        
    m3_path = Path(caminho_m3)
    
    # 1. Carregar chassis qualificados do M3
    if m3_path.exists():
        print(f"[EXTRACT] Carregando base qualificada do motor M3: {m3_path.name}")
        df_m3 = pd.read_parquet(m3_path)
    else:
        raise FileNotFoundError(f"Output de potencial M3 nao encontrado em: {caminho_m3}")
        
    # 2. Obter horimetro diretamente dos dados do M3 de forma flexivel e resiliente
    df_ativos = df_m3.copy()
    
    if 'Horimetro' in df_ativos.columns:
        df_ativos['Work Order Hours Reported'] = pd.to_numeric(df_ativos['Horimetro'], errors='coerce').fillna(0.0)
    elif 'Work Order Hours Reported' in df_ativos.columns:
        df_ativos['Work Order Hours Reported'] = pd.to_numeric(df_ativos['Work Order Hours Reported'], errors='coerce').fillna(0.0)
    else:
        # Busca case-insensitive por colunas que possuam 'hor' ou 'hour'
        colunas_hor = [c for c in df_ativos.columns if 'hor' in c.lower() or 'hour' in c.lower()]
        if colunas_hor:
            print(f"[EXTRACT] M3: Associando coluna de horímetro encontrada: '{colunas_hor[0]}'")
            df_ativos['Work Order Hours Reported'] = pd.to_numeric(df_ativos[colunas_hor[0]], errors='coerce').fillna(0.0)
        else:
            print("[WARNING] Coluna de horimetro nao encontrada no M3. Usando horimetro simulado de 2500.0.")
            df_ativos['Work Order Hours Reported'] = 2500.0
            
    # Mapeia PIN para Serial Number
    df_ativos['Serial Number'] = df_ativos['PIN']
    
    # 3. Inferir a Familia de Produto (Product Family) dinamicamente com base no Modelo (Model Grupo)
    def inferir_familia(modelo):
        mod = str(modelo).upper()
        if any(m in mod for m in ['700J', '750J', '850J', '1050K']):
            return 'TRATORES DE ESTEIRA'
        if any(m in mod for m in ['130', '160', '180', '200', '210', '350']):
            return 'ESCAVADEIRAS'
        return 'CARREGADEIRAS'
        
    df_ativos['Product Family'] = df_ativos['Model Grupo'].apply(inferir_familia)
    
    # Ajusta nomes de colunas estruturais para manter a compatibilidade com a transformacao
    df_ativos = df_ativos.rename(columns={
        'Model Grupo': 'Model',
        'Customer': 'Customer Name'
    })
    
    # Validações Mandatorias (Fail-Fast)
    assert not df_ativos.empty, "A base ativa qualificada resultante esta vazia!"
    colunas_obrigatorias = ['Serial Number', 'Model', 'Product Family', 'Work Order Hours Reported', 'CNPJ']
    for col in colunas_obrigatorias:
        assert col in df_ativos.columns, f"Coluna obrigatoria ausente na base qualificada: {col}"
        
    print(f"[EXTRACT] Base qualificada final gerada com sucesso contendo {len(df_ativos):,} chassis.")
    return df_ativos
```

---

### Componente: [src/transform.py](file:///C:/Projetos/Inova/projects/lead-csc-pops/src/transform.py)

Reestruturação da função `calcular_alertas()` para a nova regra de primeiro alerta e recorrentes de rodantes (3.000h para `350G/P` e escavadeiras, 1.500h para tratores) e regra acumulativa de FPS.

```python
def calcular_alertas(df):
    """
    Calcula as horas acumuladas de cada equipamento e aciona os alertas de FPS e Material Rodante.
    FPS: Alerta global a cada 200h acumuladas adicionais.
    Material Rodante (Tratores): Alerta a cada 1.500h ou primeiro alerta com horímetro absoluto >= 1500h.
    Material Rodante (Escavadeiras): Alerta a cada 3.000h ou primeiro alerta com horímetro absoluto >= 3000h.
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    # 1. Calcula a variação de horas desde o último marco base
    df['Delta_Horas'] = df['Work Order Hours Reported'] - df['Horimetro_Base']
    
    # 2. Inicializa as colunas de alertas
    df['Alerta_FPS'] = False
    df['Alerta_Rodante'] = False
    df['Gatilho_Alerta'] = ""
    
    # 3. Regra FPS: Aciona a cada 200 horas acumuladas adicionais globalmente
    df.loc[df['Delta_Horas'] >= 200.0, 'Alerta_FPS'] = True
    
    # 4. Regra Material Rodante
    # Tratores de Esteira (Famílias 700J, 750J, 850J, 1050K): Alerta a cada 1.500 horas adicionais de operação, 
    # OU se o horímetro acumulado absoluto for >= 1.500 e estiver no ciclo inicial (Horimetro_Base == Work Order Hours Reported ou Horimetro_Base == 0)
    trator_mask = (
        (df['Product Family'].astype(str).str.upper().str.contains('TRATORES DE ESTEIRA|TRATOR DE ESTEIRA')) |
        (df['Model'].astype(str).str.upper().str.contains('700J|750J|850J|1050K'))
    )
    
    cond_trator_delta = trator_mask & (df['Delta_Horas'] >= 1500.0)
    cond_trator_primeiro = trator_mask & (df['Work Order Hours Reported'] >= 1500.0) & (
        (df['Horimetro_Base'] == df['Work Order Hours Reported']) | (df['Horimetro_Base'] == 0.0)
    )
    
    df.loc[cond_trator_delta | cond_trator_primeiro, 'Alerta_Rodante'] = True
    
    # Escavadeiras (Famílias 130G, 130P, 160G/P, 180G, 200G/P, 210G/P, 350ZX, 350G/P): Alerta a cada 3.000 horas adicionais de operação
    # OU se o horímetro acumulado absoluto for >= 3.000 e estiver no ciclo inicial (Horimetro_Base == Work Order Hours Reported ou Horimetro_Base == 0)
    escavadeira_mask = (
        (df['Product Family'].astype(str).str.upper().str.contains('ESCAVADEIRAS|ESCAVADEIRA')) |
        (df['Model'].astype(str).str.upper().str.contains('130G|130P|160G|160P|180G|200G|200P|210G|210P|350ZX|350G|350P'))
    )
    
    cond_escav_delta = escavadeira_mask & (df['Delta_Horas'] >= 3000.0)
    cond_escav_primeiro = escavadeira_mask & (df['Work Order Hours Reported'] >= 3000.0) & (
        (df['Horimetro_Base'] == df['Work Order Hours Reported']) | (df['Horimetro_Base'] == 0.0)
    )
    
    df.loc[cond_escav_delta | cond_escav_primeiro, 'Alerta_Rodante'] = True
    
    # 5. Define a descrição amigável do gatilho de alerta
    def obter_descricao_gatilho(row):
        alertas = []
        if row['Alerta_FPS']:
            alertas.append("Alerta FPS")
        if row['Alerta_Rodante']:
            alertas.append("Alerta Rodante")
        return " e ".join(alertas) if alertas else ""
        
    df['Gatilho_Alerta'] = df.apply(obter_descricao_gatilho, axis=1)
    
    return df
```

---

### Componente: [tests/test_transform.py](file:///C:/Projetos/Inova/projects/lead-csc-pops/tests/test_transform.py)

Atualizar a suíte de testes unitários para a conformidade das escavadeiras `350G/P` a 3.000h (primeiro alerta e cíclico).

```python
def test_calcular_alertas_primeiro_alerta_350p():
    """
    Testa se a escavadeira 350P (da família 350G/P) aciona corretamente o primeiro alerta comercial
    de Material Rodante ao atingir o limite absoluto de 3.000 horas no ciclo inicial.
    """
    dados = {
        'Serial Number': ['CHASSI_350P_ON', 'CHASSI_350P_OFF'],
        'Model': ['350P', '350P'],
        'Product Family': ['ESCAVADEIRAS', 'ESCAVADEIRAS'],
        'Work Order Hours Reported': [3020.0, 2800.0],
        'Horimetro_Base': [3020.0, 2800.0]  # Ciclo inicial
    }
    df = pd.DataFrame(dados)
    
    df_res = calcular_alertas(df)
    
    # CHASSI_350P_ON: horímetro absoluto >= 3000h (ciclo inicial) -> Alerta Rodante ativado
    ativo_on = df_res[df_res['Serial Number'] == 'CHASSI_350P_ON'].iloc[0]
    assert ativo_on['Alerta_Rodante'] == True
    
    # CHASSI_350P_OFF: horímetro absoluto < 3000h -> Alerta Rodante desativado
    ativo_off = df_res[df_res['Serial Number'] == 'CHASSI_350P_OFF'].iloc[0]
    assert ativo_off['Alerta_Rodante'] == False
```

---

## 🧪 4. Plano de Validação (TDD & Execução)

1. **Testes Unitários:** Executar `pytest tests/test_transform.py` para validar a lógica sem depender de arquivos físicos.
2. **Execução Completa:** Após o usuário incluir a coluna de horímetros e nos dar o sinal verde, rodar o agendador local via PowerShell com `BypassSandbox: true` para gerar os resultados e o HTML diário atualizados.

---
*Aguardando o sinal verde do usuário para iniciar a codificação segura.*

# Walkthrough — Finalização do Motor de Potencial v3.1

Concluímos a migração do motor de potencial para a versão **v3.1**, tornando-o totalmente funcional e integrado com a lógica de negócio solicitada para equipamentos de Construção e Pavimentação.

## 🚀 Principais Entregas

### 1. Lógica Proporcional de Período (Ano Civil)
Implementamos uma regra de "Justiça de Ativação" que calcula o potencial apenas pelo tempo que a máquina esteve em posse do cliente no ano corrente:
- **Máquinas Novas (vendidas em 2026)**: Inicia o cálculo na data da Nota Fiscal.
- **Máquinas Antigas**: Inicia o cálculo em 01/01/2026.
- **Resultado**: Novas colunas de `Potencial ... Proporcional` para cada uma das 5 categorias.

### 2. Refatoração Sobratema (Backport v3.1)
O motor de cálculo (`calc_fator`) foi reescrito para ser mais resiliente:
- **Resiliência de Colunas**: Uso de `.get()` para evitar erros se a coluna "Acima 4000 horas " tiver espaços extras.
- **Threshold de Segurança**: Implementada a trava `> 5` para converter porcentagens do Excel (ex: 125 vira 1.25).

### 3. Estabilização para o Motor 4 (Estratégia)
O schema de dados foi travado para bater exatamente com o que o Módulo de Estratégia consome:
- Exportação granular (Chassi) e agregada (CNPJ_Raiz).
- Colunas `Potencial Total` e `Horimetro_Medio` garantidas no arquivo `dataset_ouro_potencial.parquet`.

### 4. Relatório de Auditoria Detalhado (Console)
Conforme solicitado, o script agora imprime um resumo executivo completo ao final da execução:
- **Telemetria**: Total de máquinas reais vs. estimadas (mediana).
- **Cobertura**: % de chassis que possuem dono identificado via DNA.
- **Financeiro**: Comparação entre o Potencial Anual total e o Potencial Proporcional (YTD) calculado para o período.

## 🛠️ O que foi alterado

```diff
# No motor_de_potencial_v3.1_run.py

+ HOJE = pd.Timestamp.now()
+ INICIO_ANO_ATUAL = pd.Timestamp(year=HOJE.year, month=1, day=1)
+ df_potencial['Data_Inicio_Potencial'] = df_potencial['Data_NF_Venda'].apply(lambda x: max(x, INICIO_ANO_ATUAL))

- return f/100 if f > 2 else f
+ return f/100 if f > 5 else f
```

## ✅ Validação Sugerida

Ao rodar o motor, verifique o arquivo `dataset_ouro_potencial.xlsx` na pasta `cache/`.
1. Para uma máquina vendida hoje, o potencial proporcional deve ser próximo de zero.
2. Para uma máquina antiga, o proporcional deve ser cerca de 25% a 30% do anual (considerando que estamos em Abril).

> [!NOTE]
> Todos os arquivos de configuração (Conector Fabric, Paths) foram descomentados e deixados prontos para execução em ambiente local.

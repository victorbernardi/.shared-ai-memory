# 🚀 Plano de Execução Técnica: Refatoração da Carga Inicial e Ranges de Alerta

> **Identidade do Documento:** `./docs/plans/plan_v1_carga_inicial_ranges.md`  
> **Data:** 28/05/2026  
> **Status:** STANDBY (Aguardando Aprovação do Usuário)  
> **Referência:** [Especificação Carga Inicial](file:///C:/Projetos/Inova/projects/lead-csc-pops/docs/specs/2026-05-28-carga-inicial-horimetro.md)  
> **Autores:** Antigravity (Engenheiro de Software)

---

## 🎯 1. Objetivo Técnico

Implementar a orquestração robusta de **Carga Inicial (Bootstrap)** por parâmetro de console no motor `lead-csc-pops`, permitindo que apenas os chassis dentro dos ranges rígidos de tolerância de horímetro absoluto gerem alertas no primeiro lote. O plano engloba a unificação do range de Tratores para 500h de tolerância em todos os gatilhos, a separação de escopos no `run.py`, e a execução do workflow TDD (Test-Driven Development) para assegurar conformidade matemática.

---

## 🏗️ 2. Arquitetura das Alterações Propostas

### 1. `src/transform.py` (Camada 2 - Lógica Pura)

* **Modificação:** Simplificar e corrigir a regra de Material Rodante para Tratores no modo Bootstrap (`carga_inicial=True`) para aplicar o range de tolerância unificado de 500h desde o primeiro gatilho de 1.500h.
* **Código Esperado:**

    ```python
    df.loc[trator_mask & (h >= 1500.0) & ((h % 1500.0) <= 500.0), 'Alerta_Rodante'] = True
    ```

### 2. `tests/test_transform.py` (Camada de Testes)

* **Modificação:** Ajustar o caso de teste `test_calcular_alertas_carga_inicial_bootstrap` para refletir as novas regras acordadas com o Victor:
  * Um trator com 1.800h (antes daria False com tolerância de 200h) deve retornar `Alerta_Rodante = True` (está no range `[1500-2000]`).
  * Um trator com 2.200h deve retornar `Alerta_Rodante = False` (está fora de todos os ranges).

### 3. `run.py` (Camada 4 - Orquestrador)

* **Modificação:**
  * Registrar o argumento `--carga-inicial` no `argparse`.
  * Remover a lógica anterior de desativação automática (`if media_horimetro > 500: carga_inicial = False`).
  * Definir que quando `--carga-inicial` for ativado:
        1. O script zera e atualiza os horímetros base de 100% dos chassis lidos do M3 para seus horímetros atuais no arquivo de estado parquet.
        2. Chama a transformação com `carga_inicial=True` usando o horímetro absoluto para filtrar os leads.
  * Quando `--carga-inicial` for omitido:
        1. O script opera normalmente no modo Produção (`carga_inicial=False`), calculando os alertas baseando-se no delta do estado histórico de cada máquina.
        2. Mantém a reentrada automática do feedback comercial vindo do Excel anterior, atualizando as bases históricas de quem foi tratado ("Venda" ou "Venda Perdida").

---

## 📝 3. Checklist Atômico de Tarefas (Work Breakdown Structure)

* [ ] **Passo 1 (TDD RED):** Modificar `tests/test_transform.py` com as novas asserções de ranges de tratores e rodar o suite de testes para verificar falha.
* [ ] **Passo 2 (TDD GREEN):** Implementar a simplificação da regra em `src/transform.py` e rodar os testes até obter aprovação verde completa (16/16 testes passando).
* [ ] **Passo 3 (ORQUESTRADOR):** Injetar o argumento `--carga-inicial` e a lógica de transição limpa em `run.py`.
* [ ] **Passo 4 (MARCO ZERO):** Deletar o arquivo de estado temporário legado `data/output/horimetro_base_estado.parquet`.
* [ ] **Passo 5 (DRY-RUN BOOTSTRAP):** Rodar a carga inicial no console (`python run.py --carga-inicial`) e auditar o output Excel.
* [ ] **Passo 6 (DRY-RUN PRODUÇÃO):** Rodar a execução de produção subsequente (`python run.py`) para simular a estabilidade (deve resultar em 0 novos leads adicionados, pois as bases foram marcadas na carga inicial e não houve alteração no M3 ainda).
* [ ] **Passo 7 (VERIFICAÇÃO FINAL):** Garantir que os arquivos compilados atendam às diretrizes de higiene física (sem lixo) e documentação de walkthrough atualizada.

---

## 🧪 4. Plano de Validação e Critérios de Aceitação

### Testes Automatizados

```powershell
# Executar a suíte de testes unitários local
pytest tests/test_transform.py -v
```

*Critério de Aceitação:* Todos os testes terminam com status `PASSED` sem regressões lógicas.

### Teste de Sistema Completo (Simulação Real)

1. **Carga Inicial:**
    * Executar `python run.py --carga-inicial`.
    * *Resultado esperado:* O arquivo `horimetro_base_estado.parquet` deve ser criado contendo 2.991 chassis com `Horimetro_Base` igual ao horímetro absoluto atual de cada um.
    * A planilha Excel final de leads deve conter **apenas** os chassis que caíram nos ranges de tolerância absoluto das carregadeiras (FPS), tratores (MR) e escavadeiras (MR).
2. **Modo de Produção:**
    * Executar `python run.py`.
    * *Resultado esperado:* Nenhuma nova linha de lead em aberto deve ser gerada (0 leads adicionais), confirmando que a base histórica de deltas está perfeitamente sincronizada com o M3 e que não há ruído.

---

## 🛡️ 5. Governança e Segurança

* **Trava de Segurança (STANDBY MODE):** O engenheiro de IA está em modo standby. Nenhuma linha de código será alterada até a aprovação formal do Victor nesta especificação e plano técnico de execução.

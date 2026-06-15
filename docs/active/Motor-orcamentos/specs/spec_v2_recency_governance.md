# Especificação Técnica v2: Governança de Recência e Integração no Pipeline (Motor de Orçamentos)

## 1. Escopo e Objetivos
O objetivo desta especificação é formalizar a integração do **Motor de Orçamentos** (`08_Motor_Orcamentos`) à malha de governança e recência do ecossistema Inova. Isso envolve:
1. Automatizar a verificação prévia de recência (Pre-flight Check) e a atualização do relatório de recência (Post-flight Actuator) dentro de `Motor-orçamentos/run.py`.
2. Substituir as fontes de dados manuais de "Orçamentos Abertos" e "Orçamentos Cancelados" no relatório centralizado de recência (`shared/generate_recency_report.py`) pelas saídas automatizadas do motor.
3. Adicionar o Motor de Orçamentos ao orquestrador principal do pipeline (`ligar_motores.py`) para execução ponta a ponta.

---

## 2. Alterações na Governança de Recência (`shared/generate_recency_report.py`)
Atualmente, as fontes de Orçamentos Abertos e Cancelados são tratadas como insumos manuais na pasta `shared/data/`.
Com a automação do Motor de Orçamentos, as fontes devem ser redefinidas para:
* **Orçamentos Abertos**:
  * Novo Caminho: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\data\output\orcamentos_abertos_enriquecidos.xlsx`
  * Propriedade `manual`: `False`
  * Exibição: `orcamentos_abertos_enriquecidos.xlsx`
* **Orçamentos Cancelados**:
  * Novo Caminho: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\data\output\tabela_orçamentos_cancelados.xlsx`
  * Propriedade `manual`: `False`
  * Exibição: `tabela_orçamentos_cancelados.xlsx`

---

## 3. Integração de Pre-flight e Post-flight no Motor (`Motor-orçamentos/run.py`)
Seguindo o padrão implementado no Motor M2 (Faturamento):
* **Pre-flight Check**: No início do processamento, o script deve validar o ambiente e checar a recência das demais fontes necessárias rodando a rotina `run_preflight` localizada em `shared/governance_sensor.py`.
* **Post-flight Actuator**: Após concluir as extrações e salvar as planilhas enriquecidas com sucesso, o script deve invocar o `shared/generate_recency_report.py` para gerar o relatório atualizado de recência, refletindo a nova data de modificação dos arquivos gerados.

---

## 4. Orquestração no Pipeline (`pipelines/potencial-clientes/ligar_motores.py`)
O Motor de Orçamentos deve ser incluído na esteira de orquestração automatizada como a 8ª etapa:
* Nome na pipeline: `"08 - Motor Orçamentos"`
* Caminho do Script: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\run.py`
* Execução: Sequencial, ocorrendo imediatamente após a conclusão do estágio M5 (Segmentação).

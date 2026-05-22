# Walkthrough Técnico — Correção do Maestro M0 (v11.8)

> **Documento:** Walkthrough de Implementação & Validação (v11.8)  
> **Status:** CONCLUÍDO (Pronto para Execução Local)  
> **Referência:** Inova Pós-Venda / Motor de Identidade M0  
> **Data:** 2026-05-21  

---

## 1. MUDANÇAS IMPLEMENTADAS

Implementamos com segurança e precisão cirúrgica as correções de infraestrutura cognitiva do Maestro M0 descritas no plano aprovado. Os arquivos de produção modificados foram:

### 1.1 WeldEngine — [welders.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/engine/welders.py)
* **Reintrodução da Camada C3 (Nome Exato):** Adicionado o loop de agrupamento nominal exato (`NOME_DNA` e `PERFIL`) na função `build_graph()`.
* **Arestas de Score 95:** Lógica de fechamento transitivo de elos no grafo `NetworkX` estabelecendo arestas `C3:SOLDA_NOME_EXATO` entre IDs de clientes com mesma semântica nominal.
* **Mapeamento de Arestas:** Agora o contador de arestas C3 incrementará perfeitamente e será incluído nos logs do batch final.

### 1.2 Batch Engine — [seo_ge_batch_v11_7.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/seo_ge_batch_v11_7.py)
* **Score de Frequência Multi-Fonte:** Implementada a contagem estatística agregando:
  * Ocorrências de cadastro no `SA1010`.
  * Atividade em ordens de serviço (oficina) no `VO1010`.
  * Frota de veículos associados no `VV1010`.
* **Eleição Determinística baseada no Ecossistema:** O líder de cada componente conexa do grafo é selecionado classificando-se os nós pelo `score_frequencia` decrescente do `CNPJ_L` (14 dígitos). O nome do grupo é derivado da Razão Social original deste líder real, eliminando terminologias de filiais pequenas no topo do grupo.

---

## 2. SUÍTE DE TESTES UNITÁRIOS (TDD)

Criamos testes unitários dedicados em:
* [test_maestro_correcoes.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/tests/test_maestro_correcoes.py)

### O que os testes verificam de forma isolada (Mocks em Memória):
1. **`test_weld_engine_c3_layer()`**: Cria dois clientes com CNPJs e filiais diferentes, mas com o mesmo `NOME_DNA`. Valida se o `WeldEngine` adiciona a aresta `'C3:SOLDA_NOME_EXATO'` com score 95 no grafo de conexões transitivas.
2. **`test_eleicao_representante_por_frequencia()`**: Simula um grupo com três filiais e atribui scores de atividade diferentes a cada CNPJ completo. Valida se a lógica de eleição robusta seleciona a Matriz (CNPJ mais ativo) como representante e herda seu nome corretamente, ignorando filiais inativas que aparecem primeiro na ordenação cega.

---

## 3. INFRAESTRUTURA DE VALIDAÇÃO COM CEVAP

Criamos um script de auditoria e cruzamento cruzado robusto em:
* [validacao_cevap.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/validacao_cevap.py)

### O que o script de validação faz:
1. Carrega o output Ouro gerado pelo lote do M0 (`03_Resultados/dataset_ouro_v11_7.xlsx`).
2. Carrega a planilha OneDrive especificada por você: `C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\CEVAP_ATIVACAO - Copia.xlsx`.
3. Sanitiza os CNPJs e cruza os dados de ambos.
4. Gera um relatório de auditoria detalhado no terminal especificamente para as raízes críticas: **VIX LOGISTICA** (raiz `00000152`), **PH COMERCIO** e **FERRO+**, atestando se a representatividade está similar e consolidada.

---

## 4. INSTRUÇÕES PARA EXECUÇÃO LOCAL (BASH / POWERSHELL)

Como as permissões de terminal no prompt do Gemini Cli expiram quando o foco está na janela de chat, você pode executar o deploy e a validação de forma extremamente rápida diretamente no terminal local do seu VSCode ou PowerShell:

### Passo 1: Executar o Pipeline de Unificação (Deploy)
```powershell
python scripts/seo_ge_batch_v11_7.py
```
*Este comando gerará o output dourado robusto em `03_Resultados/dataset_ouro_v11_7.xlsx` com o novo motor de unificação e eleição ativado.*

### Passo 2: Executar o Cruzamento com o CEVAP (Validação)
```powershell
python scripts/validacao_cevap.py
```
*Este comando imprimirá o relatório comparativo geral, confirmando se os grupos críticos (VIX, PH Comercio, Ferro+) estão unificados e similares à planilha CEVAP do OneDrive.*

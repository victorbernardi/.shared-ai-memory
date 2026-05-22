# Spec: Sincronização Motor Identidade v11.7 (Shared Sync)

## 1. Objetivo
Garantir que os resultados do `seo_ge_batch_v11_7.py` sejam consumidos automaticamente pelos motores downstream (Estratégia e CEVAP) através da promoção dos dados para a pasta `shared/data` seguindo o esquema de colunas legado.

## 2. Requisitos Funcionais
1. **Compatibilidade de Colunas:** O output final deve conter exatamente as colunas esperadas pelo ecossistema Inova:
   - `ID_CLIENTE`, `CNPJ_ORIGINAL`, `CNPJ_DNA`, `NOME_ORIGINAL`, `NOME_DNA`, `PERFIL`, `CNPJ_GRUPO`, `MATCH_STRATEGY`, `NOME_GRUPO_ORIGINAL`, `NOME_DNA_GRUPO`, `ID_GRUPO_MAESTRO`.
2. **Exportação Parquet:** Além do Excel local, deve gerar um arquivo `.parquet` em `C:\Projetos\Inova\shared\data\dataset_ouro_identidade.parquet`.
3. **Paths Relativos:** Utilizar `shared/config.py` para definir os caminhos, evitando caminhos hardcoded de máquina local.

## 3. Mapeamento de Colunas (Schema Ouro)
| Origem (v11.7) | Destino (Ouro) | Regra |
| :--- | :--- | :--- |
| `ID_CLIENTE` | `ID_CLIENTE` | Direto |
| `A1_CGC` | `CNPJ_ORIGINAL` | Direto |
| `CNPJ_DNA` | `CNPJ_DNA` | Direto |
| `A1_NOME` | `NOME_ORIGINAL` | Direto |
| `NOME_DNA` | `NOME_DNA` | Direto |
| `PERFIL` | `PERFIL` | Direto |
| `CNPJ_GRUPO` | `CNPJ_GRUPO` | Direto |
| `MATCH_STRATEGY` | `MATCH_STRATEGY` | Direto |
| (Novo) | `NOME_GRUPO_ORIGINAL` | Nome do líder do grupo (sem prefixo "GRUPO") |
| (Novo) | `NOME_DNA_GRUPO` | DNA do líder do grupo |
| (Novo) | `ID_GRUPO_MAESTRO` | "M0-" + `CNPJ_GRUPO` |

## 4. Plano de Validação
1. **Teste de Schema:** Verificar se o arquivo gerado possui as 11 colunas exigidas.
2. **Teste de Integridade:** Garantir que o número de registros no `.parquet` seja igual ao do `.xlsx` local.
3. **Teste de Consumo:** Rodar uma inspeção rápida no `Motor Estratégia` para garantir que ele consegue ler o novo arquivo sem erros de KeyError.

## 5. Riscos
- **Quebra de Downstream:** Se faltar qualquer coluna, o `motor_de_estrategia_v1.py` falhará.
- **Data Clashing:** Sobrescrever o arquivo compartilhado com dados parciais (QSA incompleto). *Mitigação: Manter backup antes de sobrescrever.*

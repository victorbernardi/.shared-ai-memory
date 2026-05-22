# Walkthrough: Sincronização Motor Identidade v11.7 (Shared Sync)

## 🏁 Objetivo Alcançado
Estabelecemos a ponte automática entre a inteligência de grafos do **SEO_GE (v11.7)** e os motores downstream (**CEVAP** e **Estratégia**). O Motor Identidade agora promove seus resultados para a área compartilhada no formato e schema exigidos.

## 🛠️ Mudanças Realizadas

### 1. Script `seo_ge_batch_v11_7.py`
- **Integração Shared:** Adicionado suporte ao `SHARED_DATA` via `shared/config.py`.
- **Hotfix de Caminhos:** Implementada resolução robusta para localizar arquivos de cache em `shared/data`, `./data/` e `Downloads` (para o arquivo POPS).
- **Exportação Dupla:** 
    - **Local (.xlsx):** Mantido para auditoria interna e uso das ferramentas `seo_ge_scanner` e `audit_tool`.
    - **Shared (.parquet):** Gerado com o "Schema Ouro" (11 colunas) para produção.
- **Backup:** Implementada rotina de backup preventivo (`.parquet.bak`) antes da sobrescrita do arquivo mestre.

### 2. Normalização de Schema (M0)
Implementada a função `transform_to_ouro_schema` que garante as seguintes transformações:
- `A1_CGC` ➔ `CNPJ_ORIGINAL`
- `A1_NOME` ➔ `NOME_ORIGINAL`
- Criação de `ID_GRUPO_MAESTRO` (Padrão "M0-XXXXXXXX")
- Limpeza de prefixos "GRUPO " em `NOME_GRUPO_ORIGINAL`.

## 🧪 Validação e Testes
- **TDD:** Desenvolvidos testes unitários em `tests/test_shared_sync.py` para validar a importação de configs e a lógica de mapeamento de colunas.
- **Verificação Empírica:** Execução completa do batch confirmando a gravação de **2748 registros** no laboratório e a sincronização do Parquet compartilhado.
- **Schema Check:** Confirmado que o arquivo final possui as 11 colunas rigorosamente idênticas ao script legado.

## 🚀 Próximos Passos
- Agora que o `dataset_ouro_identidade.parquet` está atualizado, você pode rodar o **Motor de Estratégia (M5)** para propagar as mudanças para o CEVAP.
- O script `motor_identidade_m0.py` pode ser movido para a pasta de arquivos legados.

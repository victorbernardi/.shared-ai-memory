# Spec V5 - Redirecionamento e Migração de Backups do Motor CEVAP

> **Histórico de Versões:**
> - v1: Motor CEVAP Inicial
> - v2: Ajuste de Colunas
> - v3: Conformidade de Negócio
> - v4: Integração Final e OneDrive
> - **v5: Redirecionamento de Backups (Atual)**

---

## 1. Objetivo

Ajustar o Motor CEVAP para que os backups históricos da planilha de ativação sejam salvos e armazenados localmente dentro da pasta do projeto, evitando poluir o diretório de Documentos do OneDrive do usuário. Além disso, migrar com segurança 65 arquivos históricos atualmente presentes no OneDrive para a nova pasta local de backups e implementar testes que validem a migração.

---

## 2. Requisitos

### Requisitos Funcionais
*   **RF1 - Migração Segura:** Desenvolver um script que mova 65 arquivos (62 backups históricos padrão `CEVAP_ATIVACAO_backup_*` + 3 cópias temporárias) do OneDrive do usuário para a pasta de dados do projeto.
*   **RF2 - Validação de Integridade pós-migração:** O script de migração deve validar que o arquivo foi copiado com sucesso e que o tamanho no destino é exatamente igual ao original antes de removê-lo da origem (OneDrive).
*   **RF3 - Alteração do Motor:** Modificar `consolidate_cevap.py` para que os futuros backups da planilha do OneDrive sejam gravados na pasta `data/backups/` do projeto.
*   **RF4 - Proteção da Planilha Principal:** O arquivo ativo `CEVAP_ATIVACAO.xlsx` no OneDrive não deve ser removido nem afetado pelo script de migração ou alteração do motor.

### Requisitos Não-Funcionais
*   **RNF1 - Portabilidade de Caminhos:** O script de migração e o motor devem utilizar a biblioteca `pathlib` e caminhos relativos ao arquivo do script (`_Path(__file__).parents[n]`) para obter o diretório do projeto, sem strings absolutas hardcoded.
*   **RNF2 - Tratamento de Erros:** Arquivos bloqueados ou em uso devem ser reportados e ignorados na migração (não deletados da origem) para evitar perda de dados.
*   **RNF3 - Idempotência:** A execução repetida do script de migração ou dos testes não deve corromper dados, gerar duplicados ou causar erros se os arquivos já tiverem sido movidos.

---

## 3. Arquitetura e Estrutura de Arquivos

### Mudanças Estruturais
```
motor-cevap/
├── data/
│   └── backups/                  <-- Nova pasta local para armazenar os backups
├── docs/
│   └── specs/
│       └── spec_v5_redirecionamento_backups.md  <-- Esta especificação
├── scripts/
│   ├── consolidate_cevap.py      <-- Alterado para salvar em data/backups/
│   └── migrate_cevap_backups.py  <-- Novo script para executar a migração segura
└── tests/
    └── test_backup_migration.py  <-- Novo teste de validação (unitário + real)
```

### Lista de 65 Arquivos a Mover
*   **62 Backups padrão `CEVAP_ATIVACAO_backup_*.xlsx/.xlsm`:**
    *   `CEVAP_ATIVACAO_backup_20260522_1018.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1051.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1055.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1059.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1106.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1255.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260522_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260526_0807.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260526_0824.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260526_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260527_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260528_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260529_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1114.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1128.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1129.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1130.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1132.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1133.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1134.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260601_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1443.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1445.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1446.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1939.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1940.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1941.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1942.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1943.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_1948.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260602_2002.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0212.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0223.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0257.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0300.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0308.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0319.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0334.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_0340.xlsm`
    *   `CEVAP_ATIVACAO_backup_20260603_0359.xlsm`
    *   `CEVAP_ATIVACAO_backup_20260603_0404.xlsm`
    *   `CEVAP_ATIVACAO_backup_20260603_0409.xlsm`
    *   `CEVAP_ATIVACAO_backup_20260603_0415.xlsm`
    *   `CEVAP_ATIVACAO_backup_20260603_1207.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_1215.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_1222.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260603_1740.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0838.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0947.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0953.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0954.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0957.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0958.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_0959.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1001.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1003.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1005.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1007.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1018.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1019.xlsx`
    *   `CEVAP_ATIVACAO_backup_20260608_1020.xlsx`
*   **3 Cópias temporárias adicionais:**
    *   `CEVAP_ATIVACAO - 090526.xlsx`
    *   `CEVAP_ATIVACAO - Copia.xlsx`
    *   `CEVAP_ATIVACAO - Copia (2).xlsx`

---

## 4. Validação (Plano de Testes)

Para comprovar empírica e formalmente a qualidade e a corretude da migração:

1.  **Execução do Teste Unitário (Simulado):** 
    *   O pytest criará diretórios virtuais temporários contendo arquivos fictícios simulando os 65 backups.
    *   Testará a rotina de movimentação e garantirá que a integridade foi preservada.
    *   Validará que em caso de interrupção ou arquivo bloqueado, o sistema é resiliente.
2.  **Validação Real Pós-Migração:** 
    *   Executar o script `scripts/migrate_cevap_backups.py`.
    *   Executar o teste `pytest tests/test_backup_migration.py -v`.
    *   O teste validará no ambiente do usuário que a pasta do OneDrive está limpa de backups, e que os 65 arquivos estão de fato em `data/backups/` e que a planilha `CEVAP_ATIVACAO.xlsx` continua íntegra no OneDrive.

---

## 5. Log de Decisões

*   **Decisão 1:** Manter todos os backups (sem limpeza temporal automática) a pedido do usuário.
*   **Decisão 2:** Mover as 3 cópias temporárias que não seguem o padrão exato de nomenclatura do backup junto com os outros 62 arquivos oficiais de backup.
*   **Decisão 3:** A planilha ativa de trabalho (`CEVAP_ATIVACAO.xlsx`) não possui proteção de senha e deve permanecer na origem sem alterações de segurança.

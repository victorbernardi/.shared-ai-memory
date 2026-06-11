# Especificação Técnica - Correção de Travas na Planilha de Leads (v1)

## 1. Contexto do Problema
O usuário relatou que a planilha gerada pelo pipeline (`lead-csc-pops`) está com as colunas editáveis "Retorno do Contato" (coluna O / 15) e "Observações" (coluna P / 16) bloqueadas para modificação. Isso impede que a equipe comercial de pós-vendas registre o feedback das tratativas comerciais.

## 2. Análise do Código e Causa Raiz
Ao analisar a camada de carregamento (`src/load.py`), identificamos que a planilha é gerada do zero utilizando a biblioteca `openpyxl`.
O código atual tenta definir a propriedade de desbloqueio (`Protection(locked=False)`) individualmente em cada célula das linhas geradas durante o processamento do DataFrame de dados:

```python
        # Colunas editáveis (15 e 16) — Amarelo Ouro
        c_retorno = ws.cell(row=row_idx, column=15, value=retorno)
        c_retorno.protection = unlocked_protection
        # ...
        c_obs = ws.cell(row=row_idx, column=16, value=obs)
        c_obs.protection = unlocked_protection
```

Entretanto, esse comportamento apresenta limitações:
1. **Comportamento das Colunas Inteiras:** Células que ficam abaixo da última linha de dados processada (ou células novas que o usuário tenta adicionar) permanecem com o estilo de proteção padrão (`locked=True`). Sob a proteção ativa da folha (`ws.protection.sheet = True`), o Excel bloqueia qualquer edição nessas linhas adicionais.
2. **Atualização do Power Query:** Na planilha final de produção (`leads-csc-pops-peças.xlsm`), que puxa os dados do arquivo base via Power Query, o processo de atualização de dados recria a tabela do Excel. Caso a planilha de produção esteja protegida e as colunas O e P não estejam configuradas como desbloqueadas no nível da coluna inteira da folha, o Excel re-bloqueia as células geradas.
3. **Redefinição de Borda:** Logo após aplicar a proteção nas colunas 15 e 16, o código executa:
   ```python
   ws.cell(row=row_idx, column=15).border = box_border
   ws.cell(row=row_idx, column=16).border = box_border
   ```
   Embora teoricamente independentes, no `openpyxl` redefinir propriedades de estilo de forma sequencial por chamadas repetidas a `ws.cell(...)` sem vincular a um estilo centralizado pode, dependendo da versão, sobrescrever ou redefinir a proteção do objeto de célula se o gerenciador de estilos do Excel agrupar de forma inadequada.

## 3. Critérios de Aceitação
- As colunas **O** ("Retorno do Contato") e **P** ("Observações") devem estar completamente desbloqueadas para edição por padrão (exceto o cabeçalho na linha 1).
- O cabeçalho (linha 1) deve permanecer bloqueado contra edição para preservar a integridade estrutural da planilha.
- O autofiltro e a ordenação devem permanecer habilitados.
- Nenhuma outra coluna estrutural (A a N) deve permitir edição por usuários não autorizados.

## 4. Testes de Validação
Devemos criar um teste automatizado em `tests/test_load_consultor.py` ou similar que:
1. Execute o fluxo de geração da planilha.
2. Carregue o arquivo Excel gerado.
3. Valide que as colunas O e P (linhas de dados e linhas abaixo) estão com a propriedade de proteção `locked == False`.
4. Valide que as células de cabeçalho das colunas O e P estão com `locked == True`.
5. Valide que as colunas de A a N estão com `locked == True`.

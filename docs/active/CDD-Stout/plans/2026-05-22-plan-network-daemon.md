# Plano de Implementação: V5.0 Network Daemon (`network_daemon.py`)

_Versão: 1.0.0 — 2026-05-22_

> **Para Engenheiros de IA:** REQUISITO OBRIGATÓRIO: Utilizar a skill `superpowers:subagent-driven-development` ou `superpowers:executing-plans` para implementar este plano tarefa por tarefa. As etapas devem usar checkboxes (`- [ ]`) para rastreabilidade de progresso.

## 1. Visão Geral

Este plano descreve as etapas sequenciais para projetar, construir e testar a infraestrutura de rede assíncrona do CDD V5.0. O objetivo principal é criar o `network_daemon.py` que transporta pacotes TCP assincronamente entre nós do ecossistema, comunicando-se com o `orchestrator_sync.py` puramente através de arquivos locais e respeitando as Karpathy Laws globais.

---

## 2. Mapa de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `data/config/network/routing.json` | Criar | Configuração e mapeamento de endereços IPs/Portas dos nós de rede. |
| `src/distributed/network_daemon.py` | Criar | O servidor e cliente TCP assíncrono implementado via `asyncio`. |
| `tests/test_network_daemon.py` | Criar | Testes de unidade e de integração assíncronos para o daemon de rede. |
| `skills/stout-skill-registry/registry.json` | Modificar | Registrar a nova capacidade técnica de infraestrutura CDD. |

---

## 3. Cronograma de Execução e Checklist de Progresso

### Task 1: Roteamento Estático (`routing.json`)

*Objetivo:* Definir a topologia da malha de rede para que o daemon saiba para onde disparar conexões.

- [ ] **Step 1:** Criar o arquivo `data/config/network/routing.json` contendo um exemplo de topologia com nós local e remoto:

  ```json
  {
    "nodes": {
      "local-stout-node": {
        "host": "127.0.0.1",
        "port": 8500
      },
      "remote-stout-node": {
        "host": "127.0.0.1",
        "port": 8501
      }
    }
  }
  ```text

- [ ] **Step 2:** Validar a conformidade do JSON.

---

### Task 2: Servidor TCP Assíncrono (`network_daemon.py` - Recepção)

*Objetivo:* Inicializar o escutador de soquetes, aceitar conexões simultâneas e realizar escritas atômicas de mensagens no Inbox.

- [ ] **Step 1:** Criar a estrutura básica do daemon de rede em `src/distributed/network_daemon.py` importando `asyncio`, `json`, `pathlib`, `logging` e `ProjectLink`.
- [ ] **Step 2:** Implementar a rotina assíncrona `handle_inbound_client(reader, writer)` para leitura de pacotes delimitados por `\n`.
- [ ] **Step 3:** Implementar a integração com o `ProjectLink` para validar handshakes antes da persistência física.
- [ ] **Step 4:** Implementar a escrita atômica do arquivo de handshake validado na pasta `data/network/inbox/` usando o workspace temporário `data/network/.tmp/` e `os.replace`.

---

### Task 3: Cliente TCP e Outbox Transmitter (`network_daemon.py` - Transmissão)

*Objetivo:* Monitorar a pasta Outbox, identificar arquivos de mensagens destinadas a nós remotos e enviá-las de forma assíncrona com retry exponencial.

- [ ] **Step 1:** Implementar o loop periódico assíncrono `outbox_monitor_loop()` (pooling assíncrono leve).
- [ ] **Step 2:** Implementar o decodificador de destinatários e resolvedor de endereços via `routing.json`.
- [ ] **Step 3:** Implementar a co-rotina `send_payload(node_id, payload)` que se conecta assincronamente ao nó remoto via `asyncio.open_connection()`.
- [ ] **Step 4:** Implementar a lógica de backoff exponencial e reenvio caso a conexão falhe, tolerando offline temporário.
- [ ] **Step 5:** Implementar a promoção do arquivo do outbox para a pasta `data/network/sent/` após sucesso físico no envio.

---

### Task 4: Testes Assíncronos e Validação (`tests/test_network_daemon.py`)

*Objetivo:* Garantir a estabilidade da camada assíncrona e simular a troca de mensagens E2E.

- [ ] **Step 1:** Criar o arquivo `tests/test_network_daemon.py` utilizando o plugin `pytest-asyncio` ou co-rotinas nativas de mock.
- [ ] **Step 2:** Escrever o caso de teste para o Servidor TCP validando se ele escuta, recebe um handshake JSON válido e descarrega um arquivo estruturado no Inbox.
- [ ] **Step 3:** Escrever o caso de teste para o Outbox Transmitter validando se mensagens salvas em `outbox/` são lidas, enviadas a um mock de servidor ativo e arquivadas em `sent/`.
- [ ] **Step 4:** Executar a suíte de testes assíncronos e garantir o resultado verde.

---

### Task 5: Governança, Integração no Catálogo e Registro

*Objetivo:* Registrar as capacidades do novo serviço distribuído no registry central do ecossistema.

- [ ] **Step 1:** Adicionar ao `skills/stout-skill-registry/registry.json` os metadados do `network_daemon.py` sob as capacidades de sincronização distribuída V5.
- [ ] **Step 2:** Integrar o processo do daemon na documentação executiva do `GEMINI.md` local.
- [ ] **Step 3:** Realizar a auditoria de skills utilizando `audit_skills.py`.

---

## 4. Governança Operacional (Fases de Segurança)

* **[STANDBY]** Nenhuma alteração física ou gravação em arquivos de código de produção deve ocorrer durante a fase de planejamento. O avanço para a Task 1 exige aprovação explícita e formal do usuário.
* Toda escrita em disco de arquivos novos exige a criação prévia de uma pasta de cache de isolamento sob `data/network/.tmp/` para evitar fragmentação e travar transações atômicas seguras.

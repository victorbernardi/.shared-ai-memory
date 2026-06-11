# Especificação Técnica: CDD V5.0 Network Daemon (`network_daemon.py`)

_Versão: 1.0.0 — 2026-05-22_

## 1. Escopo e Propósito

Esta especificação define o comportamento, a arquitetura e os requisitos técnicos do `network_daemon.py`, o componente de transporte assíncrono da fase **V5.0 Distributed CDD (ProjectLink)**. 

O objetivo do `network_daemon.py` é prover uma camada física de transporte de rede TCP/IP leve e resiliente entre diferentes projetos do ecossistema Stout Lab, operando de forma inteiramente assíncrona. Ele desacopla a recepção/transmissão física de rede da lógica de negócios de processamento e auditoria que reside no `orchestrator_sync.py`.

---

## 2. Arquitetura Geral

O daemon de rede opera sob o princípio de **Desacoplamento de Barramento de Arquivos (Outbox/Inbox Pattern)**:

```mermaid
graph TD
    subgraph Projeto Local
        outbox[data/network/outbox/*.json] -->|Monitorado por| daemon[network_daemon.py]
        daemon -->|Gravação Atômica| inbox[data/network/inbox/*.json]
        inbox -->|Lido e Processado por| sync[orchestrator_sync.py]
    end
    
    subgraph Projeto Remoto
        remote_daemon[network_daemon.py Remoto]
    end
    
    daemon -.->|Sockets TCP/IP Assíncronos| remote_daemon
    remote_daemon -.->|Sockets TCP/IP Assíncronos| daemon
```text

---

## 3. Requisitos Funcionais

### RF-1: Servidor TCP Assíncrono (Recepção)

* O daemon deve inicializar um servidor TCP assíncrono utilizando o módulo nativo `asyncio` do Python (`asyncio.start_server`).
* A porta e o host de escuta devem ser parametrizáveis via variáveis de ambiente:
  * `CDD_NODE_HOST` (Padrão: `127.0.0.1`)
  * `CDD_NODE_PORT` (Padrão: `8500`)
* Cada conexão recebida deve ser tratada concorrentemente em uma co-rotina assíncrona isolada.
* O stream de dados deve ser interpretado como JSON, delimitado por caracteres de quebra de linha (`\n`) para mitigar problemas de fragmentação de rede TCP.
* Ao receber um pacote:
  1. O payload deve ser decodificado como string UTF-8 e convertido para JSON.
  2. O daemon deve validar a estrutura mínima exigida pelo `v5_schema.json` utilizando a classe `ProjectLink`.
  3. Se válido, o arquivo JSON correspondente ao handshake deve ser salvo na pasta de entrada `data/network/inbox/` usando a estratégia de **Escrita Temporária + Rename Atômico (Atomic Write)** para prevenir condições de corrida.
  4. O nome do arquivo gerado deve conter o prefixo de timestamp em microssegundos e o fence token do remetente para garantir ordenação FIFO natural.

### RF-2: Monitoramento e Envio Assíncrono (Transmissão)

* O daemon deve monitorar a pasta local `data/network/outbox/` de forma assíncrona periódica (pooling assíncrono leve a cada `0.2` segundos).
* Quando arquivos `.json` forem detectados no `outbox/`:
  1. O daemon deve ler o cabeçalho do arquivo para identificar o nó remoto de destino (ex: `target_node_id` ou IP/porta explícito).
  2. O daemon deve obter o endereço (IP e Porta) do nó de destino através do gerenciador de rotas em `data/config/network/routing.json`.
  3. O daemon deve abrir uma conexão TCP assíncrona (`asyncio.open_connection`) com o destinatário.
  4. O payload JSON contendo o handshake formatado deve ser transmitido seguido do delimitador `\n`.
  5. Após a transmissão bem-sucedida, o arquivo do outbox deve ser excluído ou movido de forma atômica para uma pasta de histórico `data/network/sent/`.

### RF-3: Resiliência e Tolerância a Falhas

* **Retry com Backoff Exponencial:** Se o nó de destino estiver temporariamente offline, o daemon deve enfileirar o arquivo novamente no outbox para reenvio e aplicar uma estratégia de retry exponencial (ex: 2s, 4s, 8s...) até o limite de `MAX_NETWORK_RETRIES` (Padrão: `5`).
* **Isolamento de Dead Letter Network (DLN):** Se o limite de retries expirar, o arquivo deve ser movido para a pasta `data/network/dead_letter/` enriquecido com um envelope de erro especificando a falha de comunicação física.
* **Graceful Shutdown:** Suporte a encerramento limpo via sinais `SIGINT` e `SIGTERM` garantindo que nenhuma transmissão ativa ou gravação de arquivo pendente seja interrompida no meio do caminho.

---

## 4. Estrutura de Diretórios e Fluxo de Arquivos

Para operação completa, a pasta `data/network` será estendida com novas subpastas:

* `data/network/inbox/` — Handshakes físicos recebidos e validados pelo daemon de rede.
* `data/network/outbox/` — Mensagens de saída criadas pela aplicação local destinadas aos nós da malha.
* `data/network/sent/` — Histórico de handshakes de saída transmitidos com sucesso.
* `data/network/dead_letter/` — Falhas na entrega física ou payloads corrompidos.
* `data/network/.tmp/` — Workspace temporário de escrita física.

---

## 5. Casos de Borda e Segurança

* **Detecção de Portas Ocupadas:** O daemon deve tratar graceful e logar com nível `CRITICAL` se a porta TCP de escuta estiver em uso por outro serviço, liberando os recursos associados e encerrando com código `1`.
* **Tratamento de Payload Gigante:** Limitar o buffer de leitura a `64KB` por pacote para evitar ataques de estouro de memória induzidos por dados falsos na rede.
* **Validação Rígida:** Rejeitar imediatamente qualquer stream que não seja JSON válido na camada física de transporte, enviando o log da mensagem inválida para o sandbox de auditoria local.

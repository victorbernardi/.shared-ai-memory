# 📊 Documentação Master: Motor de Potencial v3.1 (Inova)

## 📋 Controle de Versão
| Versão | Data | Autor | Descrição |
| :--- | :--- | :--- | :--- |
| v3.1 | 09/04/2026 | Antigravity | Unificação das visões técnica e de negócios. Evolução da v2.8. |

---

## 1. Sumário Executivo (Visão de Negócio)
O **Motor de Potencial v3.1** atua como a inteligência central de "Market Capacity" da Inova. Sua missão é responder: *"Quanto cada cliente deveria gastar com a Inova considerando o tamanho e a intensidade de uso de sua frota?"*. 

Nesta versão, introduzimos a **Métrica de Safra (Proporcional)**, que permite ao time comercial acompanhar o gap de vendas em tempo real, comparando o realizado contra o potencial acumulado do ano até a data presente.

---

## 2. A Fonte de Dados: O que é a Sobratema?
A **Sobratema** (Associação Brasileira de Tecnologia para Construção e Mineração) é a principal referência técnica do setor de equipamentos pesados no Brasil. 

O Motor v3.1 utiliza o **Guia de Custos de Equipamentos Sobratema**, que fornece:
- **Custo de Manutenção:** Tabelas de peças, pneus, material rodante e lubrificantes por hora trabalhada.
- **Parametrização de Mercado:** Os valores são calculados com base em estudos estatísticos de milhares de máquinas operando em solo brasileiro.
- **Credibilidade:** Ao utilizar esta métrica, a Inova não "chuta" o potencial; ela utiliza um padrão aceito por seguradoras, empreiteiras e auditorias para definir o custo operacional de cada modelo (ex: Tratores, Retroescavadeiras, Escavadeiras).

---

## 2. Fundamentação e Tratamentos (A Cozinha dos Dados)

### Bloco 1: Preparação da Frota (DNA + PoPS)
Para garantir a confiabilidade dos números, aplicamos os seguintes tratamentos:
- **Resgate de Órfãos:** Utilizamos o **Motor DNA** para identificar o dono real de máquinas que constam como "Sem Dono" no PoPS.
- **Normalização de Chassis:** Limpeza agressiva de caracteres especiais e zeros à esquerda para garantir 95.6% de acerto no match.
- **Chave Mestra (CNPJ Raiz):** Agrupamento automático de filiais dentro da matriz para visão de Grupo Econômico.

### Bloco 2: Inteligência de Horímetro (Telemetria vs. Estimado)
Nem toda máquina reporta horas. Para blindar o cálculo, adotamos:
- **Filtro de Máquinas Cegas:** Equipamentos com < 10h/ano são marcados como "Estimados".
- **Imputação por Mediana:** Máquinas cegas herdam o uso mediano de equipamentos do mesmo **Dimensionamento** e mesmo **Ano de Fabricação**.
- **Piso Técnico:** Nenhuma máquina ativa é calculada com menos de 100h/ano, evitando subestimar o potencial.

---

## 3. Metodologia de Cálculo v3.1

### 3.1 O Backport Sobratema (4 Faixas)
Corrigimos a lógica de severidade para seguir o padrão Sobratema 2024:
1. **0 - 1.000h:** Uso leve (Fator reduzido).
2. **1.001h - 2.000h:** Uso padrão (Fator 1.0).
3. **2.001h - 4.000h:** Uso pesado (Desgaste acelerado).
4. **Acima de 4.000h:** Uso severo (Troca frequente de componentes).

### 3.2 Lógica do Potencial Proporcional
Esta métrica reflete o potencial acumulado de Janeiro até Hoje.
- **Premissa de Início:** 01/01/{Ano_Corrente}.
- **Cálculo:** `(Potencial Anual / 12) * Meses_Decorridos`.
- **Objetivo:** Permitir a análise de "Pacing" (Velocidade de Vendas).

---

## 4. Glossário de Negócios e Técnico

| Termo | Definição Comercial | Detalhe Técnico |
| :--- | :--- | :--- |
| **Dimensionamento** | Categoria da máquina (ex: Retro, Trator). | Chave de VLOOKUP na 'Base Modelos'. |
| **Fator de Uso** | Severidade do ambiente de trabalho. | Multiplicador dinâmico via `calc_fator`. |
| **Dataset Ouro** | Versão final e auditada dos dados. | Arquivo Parquet/Excel consolidado no Cache. |
| **CNPJ Raiz** | Identificador do Grupo Econômico. | Extração dos 8 primeiros dígitos do CNPJ. |

---

## 5. Próximos Passos (Action Items)

| ID | Ação Recomendada | Responsável | Impacto |
| :--- | :--- | :--- | :--- |
| 01 | Migrar dashboards Power BI para apontar para a v3.1. | Time de BI | Alta Precisão |
| 02 | Validar máquinas "Órfãos" (Pendências) em campo. | Time de Serviços | Redução de 4.4% de gap |
| 03 | Atualizar o Motor Estratégico (Módulo 4) para ler a nova coluna Proporcional. | Engenharia | Visão de Safra |

---
> [!NOTE] 
> Esta documentação unifica as Skills de Arquiteto de Negócios e Técnico para fornecer uma visão 360 do projeto Inova Potencial.

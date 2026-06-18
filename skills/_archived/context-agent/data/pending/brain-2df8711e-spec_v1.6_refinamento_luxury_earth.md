# Spec Técnica v1.6 - Inova Executive Dashboard (Wave 9.0)

## 🎯 Objetivo
Ajustar o enquadramento do Hero, centralizar métricas secundárias, aplicar tags glass em valores de segmento e recalibrar a visualização do share nas filiais para atingir paridade absoluta com os requisitos do usuário.

---

## 🎨 Mudanças Visuais (UI/UX)

### 1. Hero Section (Faturamento Principal)
- **Tag Island Contexto:** Ajustar `top: -14px` e garantir que o container pai tenha `overflow: visible` para evitar o corte da tag.
- **Orbitação de Dados:**
    - O valor de faturamento do segmento (R$ Seg) deve ser movido para o **lado direito** do título "Faturamento Realizado (Mês)".
    - O valor R$ Seg e a porcentagem de atingimento Seg (14.2%) devem ser envoltos em uma classe `.glass-tag` (fundo 5% white, backdrop-filter: blur(8px)).
    - **Cores:** A porcentagem (14.2%) deve assumir a cor do título (`--text-dim` ou cinza fosco), removendo o verde direto. O valor R$ Seg mantém o Verde Saphira.
    - **Fontes:** Aumentar em 20% o tamanho das fontes dentro das tags glass.

### 2. Cards Secundários (Acumulado e Pipeline)
- **Alinhamento:** Centralizar o conteúdo vertical e horizontalmente dentro do card.
- **Texto:** Remover a palavra "ANUAL" do label "META ANUAL".

### 3. Bento Grid - Performance por Filial
- **Tipografia:** 
    - Aumentar tamanho do nome da filial (font-weight 600).
    - Aumentar label "META" e o valor da porcentagem (ex: 28%).
- **Alinhamento:** O valor monetário (R$ 44.8M) deve estar perfeitamente centralizado verticalmente entre o cabeçalho do card e a barra de progresso.
- **Dados Granulares:** Abaixo do valor principal, inserir tags glass menores replicando o estilo do Hero: `[R$ Seg] [Ating. Seg%]`.
- **Hover:** Reduzir a intensidade do `box-shadow` (glow) para um brilho âmbar técnico e sutil.

### 4. Status do Funil & Gráficos
- **Paleta de Cores:** Substituir a cor Azul Royal por um tom Âmbar/Laranja Quente (`#FF9F1A` ou `#FFB74D`).
- **Legenda:** Forçar o alinhamento das 3 legendas em uma única linha horizontal no rodapé do card.
- **Efeito Tilt:** Reduzir a sensibilidade do GSAP de `/20` para `/60` (movimento ultrassuave).

---

## ⚙️ Lógica de Dados (Engenharia)

### 1. Cálculo de Share de Contribuição
- **Nova Regra:** A barra verde deve representar o **Share de Contribuição do Segmento na Unidade** (`Realizado Segmento / Meta Total da Unidade`). Isso mostra visualmente o quanto o segmento ajudou a empurrar a barra de progresso global.

---

## 🔒 Auditoria e Proteção
1. **Spec-Validation:** Validar consistência com o SOW original.
2. **Canary Deployment:** Ativar o monitoramento de integridade no arquivo `index.html`.

---

## 🚦 Critérios de Aceite
1. Ilha do topo visível e centralizada.
2. Tags Glass aplicadas em todos os valores de segmento (Hero e Filiais).
3. Texto "ANUAL" removido.
4. Funil com cores quentes e legendas em linha.
5. Barra verde refletindo share de contribuição.

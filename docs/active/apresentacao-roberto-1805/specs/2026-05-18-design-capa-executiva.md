# Spec — Design de Capa Executiva e Redução de Carga Cognitiva

**Data:** 2026-05-18
**Projeto:** Apresentação Roberto 18/05
**Escopo:** Design visual da Capa (Imagem de Fundo + Textos PPTX)

## 1. Objetivo
Definir a arquitetura visual exata da imagem de fundo da capa e sua interação com as caixas de texto nativas do PowerPoint, garantindo **zero carga cognitiva** (legibilidade imediata) e uma estética premium de "Industrial Glassmorphism" (OLED Black + Amarelo JD).

## 2. Contexto Atual
- As imagens geradas pela IA são quadradas (1:1).
- O PowerPoint (16:9) achata imagens quadradas se usadas como `slide.background` direto sem tratamento.
- Textos brancos sobre fundos abstratos dourados/amarelos geram ruído visual e dificultam a leitura rápida.
- O usuário exige uma transposição suave da imagem abstrata para o fundo preto puro do PowerPoint.

## 3. Decisões do Brainstorming
- **Composição Visual:** [x] Opção A (Espaço Negativo à Esquerda). O lado esquerdo será preservado escuro e vazio para abrigar a tipografia. A arte pesada (Industrial Glassmorphism) ficará restrita à âncora direita.
- **Técnica de Fusão Fundo/PPTX:** [x] Opção A (Fade Direcional / Linear Scrim). O lado esquerdo e o topo desmancharão para o preto absoluto usando Python. Isso garante base escura sólida tanto para a tipografia lateral quanto para a injeção dos Logos no cabeçalho.
- **Geração Final:** (Pendente)

*(Este documento será atualizado conforme avançamos no brainstorming).*

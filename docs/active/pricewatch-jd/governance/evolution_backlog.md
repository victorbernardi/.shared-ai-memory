# Evolution Backlog

_Atualizado em 2026-05-25_

## Adaptar scraper Playwright para forçar geolocalização Brasil (SP) — impacto: medio
Quando o ML OAuth não estiver disponível, implementar fallback Playwright com geolocation={latitude: -23.5, longitude: -46.6} e locale='pt-BR' para garantir preços em BRL. Útil como plano B enquanto o app OAuth não ativa.

## Criar script de diagnóstico de saúde dos adaptadores — impacto: medio
qa_test_ml_api.py foi útil para isolar o problema de autenticação ML. Evoluir para um health_check.py genérico que testa todos os adaptadores ativos com uma peça de referência (ex: RE504836) e reporta status por adaptador.

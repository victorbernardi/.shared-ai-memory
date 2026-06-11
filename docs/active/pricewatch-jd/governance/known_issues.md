# Known Issues

_Atualizado em 2026-05-25_

## ML API requer token OAuth de usuário — client_credentials não suportado
A API do Mercado Livre Brasil retorna 400 'unsupported_grant_type' para o fluxo client_credentials. O endpoint /sites/MLB e /search retornam 403 sem Bearer token de usuário. Apenas /categories/* é público. O fluxo correto é authorization_code com redirect_uri HTTPS.

## ML DevCenter rejeita domínios próprios e www.mercadolivre.com.br como redirect URI
O formulário do DevCenter aceita https://localhost mas rejeita https://www.mercadolivre.com.br com 'O endereço deve ser válido'. Apps recém-criados levam ~24h para o servidor de auth propagar — auth.mercadolivre.com.br retorna 403 CloudFront enquanto o app não é ativado.

## Playwright ML retornava site Argentina por geolocalização de IP
Tentativas de scraping via Playwright no mercadolivre.com.br redirecionavam para o site argentino (preços em ARS) independente de locale/geolocation configurados no browser. Causa: IP geolocado fora do Brasil. Resolvido migrando para a API oficial.

## concorrentes.json com UTF-8 BOM causava JSONDecodeError
O arquivo scripts/01-mapeamento/concorrentes.json possui BOM (Byte Order Mark). Abrir com encoding='utf-8' lança JSONDecodeError. Solução: encoding='utf-8-sig' que ignora o BOM automaticamente.

## TBL Agro: URL correta é /buscar?q= não /busca?q=
A loja TBL Agro (plataforma Loja Integrada, awsli.com.br) usa /buscar?q= como endpoint de busca (confirmado via atributo action do form HTML). A URL /busca?q= retorna 404. Preços de peças JD aparecem como 'Preço sob consulta' — adaptador retorna None nesses casos.

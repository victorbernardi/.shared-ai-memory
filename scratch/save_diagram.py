import urllib.request
import base64
import zlib

mermaid_code = """
graph LR
    subgraph GESTAO["1. Gestão de Performance (Hierarquia)"]
        direction TB
        F1[FILIAL] --> CC[Centros de Custo]
        CC --> V1[Consultores]
        
        M1[Realizado] --- F1
        M2[Meta 2026] --- F1
        M3[Ano Anterior] --- F1
    end

    subgraph SEGMENTACAO["2. Quebras de Negócio (Segmentos)"]
        direction TB
        CC1[Oficina / Serviços]
        CC2[CRC]
        CC3[Contratos]
        CC4[Peças CSN]
        CC5[Peças Wirtgen]
        CC6["Peças e Acessórios (RESGATE BRANCO)"]
    end

    subgraph FUNIL["3. Funil de Vendas (Raiz Proteus)"]
        direction LR
        ORIGEM[ORIGEM: Balcão vs Oficina] --> MOV[MOVIMENTAÇÃO: Orçamentos]
        MOV --> STATUS{STATUS}
        STATUS --> S1[EM ABERTO]
        STATUS --> S2[FATURADO]
        STATUS --> S3[CANCELADO]
        
        S1 & S2 & S3 --> COMP[Comparativo: YoY / MoM]
    end

    GESTAO -.-> SEGMENTACAO
    SEGMENTACAO -.-> FUNIL
"""

# Compress and encode to use with Kroki API
data = mermaid_code.encode('utf-8')
compressed = zlib.compress(data, 9)
b64 = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/png/{b64}"

output_path = r"c:\Projetos\Inova\Metas Peças\Diagrama_BI_Performance.png"

print(f"Baixando diagrama de: {url}")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
    out_file.write(response.read())
    
print(f"✅ Diagrama salvo com sucesso em: {output_path}")

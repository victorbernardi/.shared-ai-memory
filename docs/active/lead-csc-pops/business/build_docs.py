"""
Gera PDF e DOCX da campanha com cores corrigidas, sem header/footer do browser
e com quebras de página otimizadas.
"""
import subprocess
import re
from pathlib import Path

BASE = Path(__file__).parent
BRD = BASE / "BRD-20260528-leads-csc-pops.md"
IMPACT = BASE / "IMPACT-REPORT-20260528-leads-csc-pops.md"
OUTPUT_PDF = BASE / "Campanha-Leads-Preventivos-Pos-Vendas-Inova.pdf"
OUTPUT_DOCX = BASE / "Campanha-Leads-Preventivos-Pos-Vendas-Inova.docx"
TEMP_HTML = BASE / "_temp_combined.html"
TEMP_MD = BASE / "_temp_combined.md"

CSS = """
<style>
* { box-sizing: border-box; }

@page {
  margin: 2.2cm 2cm 2cm 2cm;
}

body {
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 11pt;
  color: #1a1a1a;
  line-height: 1.65;
  max-width: 100%;
}

h1 {
  font-size: 20pt;
  color: #000000;
  border-bottom: 3px solid #FFC20E;
  padding-bottom: 8px;
  margin-top: 0;
  page-break-before: always;
}

h1:first-of-type {
  page-break-before: avoid;
}

h2 {
  font-size: 13pt;
  color: #000000;
  border-left: 4px solid #FFC20E;
  padding-left: 10px;
  margin-top: 28px;
  page-break-after: avoid;
}

/* Seções que devem iniciar em nova página */
h2:nth-of-type(4),
h2:nth-of-type(5),
h2:nth-of-type(6) {
  page-break-before: always;
}

h3 {
  font-size: 11pt;
  color: #B8860B;
  margin-top: 18px;
  page-break-after: avoid;
}

blockquote {
  background: #FFFBF0;
  border-left: 4px solid #FFC20E;
  margin: 16px 0;
  padding: 12px 16px;
  border-radius: 0 4px 4px 0;
  font-style: italic;
  color: #4a3800;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 10pt;
  page-break-inside: avoid;
}

th {
  background-color: #000000;
  color: #FFC20E;
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
}

td {
  padding: 7px 10px;
  border-bottom: 1px solid #e0e0e0;
}

tr:nth-child(even) td {
  background-color: #f9f6ef;
}

code {
  background: #f0f0f0;
  padding: 1px 5px;
  border-radius: 3px;
  font-family: "Consolas", monospace;
  font-size: 9.5pt;
}

pre {
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  font-size: 9pt;
  page-break-inside: avoid;
}

hr {
  border: none;
  border-top: 1px solid #e0d5b0;
  margin: 20px 0;
}

strong {
  color: #000000;
}

ul, ol { padding-left: 20px; }
li { margin-bottom: 4px; }

.page-break { page-break-before: always; }
</style>
"""

FOOTER_PATTERNS = [
    r"\*Documento elaborado com base na ATA de Reunião.*?\*\n?",
    r"\*Para dúvidas ou ajustes.*?\*\n?",
    r"\*Documento elaborado pela Engenharia de Dados.*?\*\n?",
    r"\*Dúvidas:.*?\*\n?",
]

def clean_markdown(text: str) -> str:
    for pattern in FOOTER_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)
    return text.strip()


def build():
    brd_text = clean_markdown(BRD.read_text(encoding="utf-8"))
    impact_text = clean_markdown(IMPACT.read_text(encoding="utf-8"))

    # DOCX: combinação limpa em markdown
    combined_md = brd_text + "\n\n---\n\n" + impact_text
    TEMP_MD.write_text(combined_md, encoding="utf-8")

    # HTML: gera via pandoc e injeta CSS customizado
    result = subprocess.run(
        [
            "pandoc", str(TEMP_MD),
            "--to", "html5",
            "-s",
            "--metadata", "title=Campanha de Leads Preventivos de Peças — Inova Máquinas",
        ],
        capture_output=True, text=True, encoding="utf-8"
    )
    html = result.stdout

    # Injeta CSS customizado após <head>
    html = html.replace("</head>", CSS + "</head>")

    # Remove o título duplicado gerado pelo pandoc no <body>
    html = re.sub(r"<h1[^>]*>Campanha de Leads Preventivos.*?</h1>\s*", "", html, count=1)

    TEMP_HTML.write_text(html, encoding="utf-8")
    print("HTML gerado.")

    # PDF via Edge headless (sem header/footer do browser)
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    subprocess.run([
        edge,
        "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={OUTPUT_PDF}",
        f"file:///{TEMP_HTML}",
    ], capture_output=True)
    size = OUTPUT_PDF.stat().st_size if OUTPUT_PDF.exists() else 0
    print(f"PDF gerado: {OUTPUT_PDF} ({size:,} bytes)")

    # DOCX via pandoc
    subprocess.run([
        "pandoc", str(TEMP_MD),
        "--to", "docx",
        "-o", str(OUTPUT_DOCX),
        "--metadata", "title=Campanha de Leads Preventivos de Peças — Inova Máquinas",
    ], capture_output=True)
    size_docx = OUTPUT_DOCX.stat().st_size if OUTPUT_DOCX.exists() else 0
    print(f"DOCX gerado: {OUTPUT_DOCX} ({size_docx:,} bytes)")

    # Limpeza
    TEMP_HTML.unlink(missing_ok=True)
    TEMP_MD.unlink(missing_ok=True)
    print("Temporários removidos.")


if __name__ == "__main__":
    build()

# Plano de Implementação: Nomenclatura Dinâmica de PDF

> **Para o Antigravity:** SUB-SKILL REQUERIDA: Use `executing-plans` para implementar este plano tarefa por tarefa.

**Objetivo:** Automatizar a criação do arquivo PDF com timestamp.

**Arquitetura:** Uso da biblioteca `datetime` para composição de string de caminho.

**Tech Stack:** Python.

---

### Tarefa 1: Implementação de Caminho Dinâmico

**Arquivos:**
- Modificar: `src/generate_pdf_report_v2.py:43`

**Passo 1: Injetar lógica de timestamp**
Substituir o `pdf_path` fixo por uma construção dinâmica.

```python
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
pdf_filename = f"Relatorio_Estrategico_JD_v5_{timestamp}.pdf"
pdf_path = os.path.join(output_dir, pdf_filename)
```

**Passo 2: Execução e Teste**
Executar: `python src/generate_pdf_report_v2.py`
Validar: Criação do arquivo físico em `docs/business/`.

**Passo 3: Commit**
Usar a skill `commit`.
Mensagem: `feat(report): implement dynamic timestamped naming for PDF output`

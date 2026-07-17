from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

EXCEL_MAX_ROWS = 1_048_576
SHEET_NAME = "Dados"


class ConversionError(ValueError):
    """Raised when a Parquet file cannot be safely exported to Excel."""


@dataclass(frozen=True)
class ConversionResult:
    input_path: Path
    output_path: Path
    rows: int
    columns: int
    sheet_name: str


def convert(input_path: Path, output_path: Path, *, overwrite: bool = False) -> ConversionResult:
    source = Path(input_path).expanduser().resolve()
    target = Path(output_path).expanduser().resolve()
    if source.suffix.lower() != ".parquet":
        raise ConversionError("O arquivo de entrada deve ter extensão .parquet.")
    if target.suffix.lower() != ".xlsx":
        raise ConversionError("O arquivo de saída deve ter extensão .xlsx.")
    if source == target:
        raise ConversionError("A entrada e a saída devem ser arquivos diferentes.")
    if not source.is_file():
        raise ConversionError(f"O arquivo de entrada não existe: {source}")
    if target.exists() and not overwrite:
        raise ConversionError(f"O arquivo de saída já existe: {target}. Confirme overwrite para substituí-lo.")

    try:
        frame = pd.read_parquet(source)
    except Exception as exc:
        raise ConversionError(f"Não foi possível ler o Parquet: {exc}") from exc
    if len(frame) > EXCEL_MAX_ROWS:
        raise ConversionError(
            f"O arquivo possui {len(frame):,} linhas; o limite do Excel é {EXCEL_MAX_ROWS:,}."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame.to_excel(target, sheet_name=SHEET_NAME, index=False, engine="openpyxl")
    except Exception as exc:
        if target.exists() and not overwrite:
            target.unlink()
        raise ConversionError(f"Não foi possível gravar o Excel: {exc}") from exc
    return ConversionResult(source, target, len(frame), len(frame.columns), SHEET_NAME)


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte Parquet para Excel em uma única aba.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    result = convert(args.input, args.output, overwrite=args.overwrite)
    print(f"[OK] {result.output_path} — {result.rows} linhas, {result.columns} colunas, aba {result.sheet_name}")


if __name__ == "__main__":
    main()

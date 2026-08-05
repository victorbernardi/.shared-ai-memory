import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import convert


def test_convert_writes_one_sheet(tmp_path):
    source, target = tmp_path / "dados.parquet", tmp_path / "dados.xlsx"
    pd.DataFrame({"codigo": [1, 2], "nome": ["A", "B"]}).to_parquet(source)
    result = convert.convert(source, target)
    assert (result.rows, result.columns, result.sheet_name) == (2, 2, "Dados")
    assert pd.ExcelFile(target).sheet_names == ["Dados"]
    assert pd.read_excel(target).to_dict("records") == [{"codigo": 1, "nome": "A"}, {"codigo": 2, "nome": "B"}]


def test_convert_rejects_invalid_extension_and_missing_source(tmp_path):
    with pytest.raises(convert.ConversionError, match="parquet"):
        convert.convert(tmp_path / "dados.csv", tmp_path / "dados.xlsx")
    with pytest.raises(convert.ConversionError, match="não existe"):
        convert.convert(tmp_path / "ausente.parquet", tmp_path / "dados.xlsx")


def test_convert_rejects_existing_output_without_overwrite(tmp_path):
    source, target = tmp_path / "dados.parquet", tmp_path / "dados.xlsx"
    pd.DataFrame({"a": [1]}).to_parquet(source)
    target.write_bytes(b"original")
    with pytest.raises(convert.ConversionError, match="já existe"):
        convert.convert(source, target)
    assert target.read_bytes() == b"original"


def test_convert_rejects_excel_row_limit_before_write(tmp_path, monkeypatch):
    source, target = tmp_path / "dados.parquet", tmp_path / "dados.xlsx"
    monkeypatch.setattr(convert, "EXCEL_MAX_ROWS", 1)
    pd.DataFrame({"a": [1, 2]}).to_parquet(source)
    with pytest.raises(convert.ConversionError, match="limite"):
        convert.convert(source, target)
    assert not target.exists()

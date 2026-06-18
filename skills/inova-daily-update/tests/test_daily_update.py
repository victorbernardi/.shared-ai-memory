#!/usr/bin/env python3
"""
tests/test_daily_update.py — Testes unitários para a skill inova-daily-update.
"""
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Adiciona o diretório scripts ao path para importação
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from check_recency import check_recency

class TestCheckRecency(unittest.TestCase):

    @patch("check_recency.RECENCY_STATUS_PATH")
    def test_file_not_found(self, mock_path):
        mock_path.exists.return_value = False
        result = check_recency()
        self.assertEqual(result, 2)

    @patch("check_recency.RECENCY_STATUS_PATH")
    def test_all_green(self, mock_path):
        mock_path.exists.return_value = True
        mock_content = """
# Relatório de Recência
| Fonte de Dados | Arquivo Físico | Status de Recência | Última Modificação |
| :--- | :--- | :--- | :--- |
| M2 (Faturamento) | f.parquet | 🟢 Atualizado Hoje | 2026-06-17 17:21 |
| M0 (Identidade) | i.parquet | 🟢 Atualizado Hoje | 2026-06-17 17:14 |
"""
        mock_path.read_text.return_value = mock_content
        result = check_recency()
        self.assertEqual(result, 0)

    @patch("check_recency.RECENCY_STATUS_PATH")
    def test_warning_yellow(self, mock_path):
        mock_path.exists.return_value = True
        mock_content = """
# Relatório de Recência
| Fonte de Dados | Arquivo Físico | Status de Recência | Última Modificação |
| :--- | :--- | :--- | :--- |
| M2 (Faturamento) | f.parquet | 🟢 Atualizado Hoje | 2026-06-17 17:21 |
| Pontuação Seedz | s.xlsx | 🟡 Desatualizado | 2026-05-13 04:25 |
"""
        mock_path.read_text.return_value = mock_content
        result = check_recency()
        self.assertEqual(result, 0) # Retorna 0 (continua com aviso)

    @patch("check_recency.RECENCY_STATUS_PATH")
    def test_critical_red(self, mock_path):
        mock_path.exists.return_value = True
        mock_content = """
# Relatório de Recência
| Fonte de Dados | Arquivo Físico | Status de Recência | Última Modificação |
| :--- | :--- | :--- | :--- |
| M2 (Faturamento) | f.parquet | 🔴 Falhou | 2026-06-17 17:21 |
"""
        mock_path.read_text.return_value = mock_content
        result = check_recency()
        self.assertEqual(result, 2) # Bloqueia retorno 2

if __name__ == "__main__":
    unittest.main()

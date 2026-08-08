import json
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path
from unittest.mock import patch

from lib.pypi_dashboard import (
    PackageMeta,
    PyPIConfig,
    build_rows,
    clickhouse_csv,
    complete_week,
    write_outputs,
)


class PypiDashboardTests(unittest.TestCase):
    def test_build_rows_fills_missing_package_inside_observed_range(self):
        raw_rows = [
            {"week_start": "2024-01-01", "project": "alpha", "downloads": "5"},
            {"week_start": "2024-01-15", "project": "alpha", "downloads": "9"},
        ]
        rows = build_rows(raw_rows, ["alpha", "beta"])
        self.assertEqual(rows, [
            {"week_start": "2024-01-01", "alpha": 5, "beta": ""},
            {"week_start": "2024-01-08", "alpha": 0, "beta": ""},
            {"week_start": "2024-01-15", "alpha": 9, "beta": ""},
        ])

    def test_first_upload_date_leaves_pre_upload_history_blank(self):
        raw_rows = [
            {"week_start": "2024-01-01", "project": "alpha", "downloads": "5"},
            {"week_start": "2024-01-15", "project": "alpha", "downloads": "9"},
            {"week_start": "2024-01-15", "project": "beta", "downloads": "2"},
        ]
        rows = build_rows(raw_rows, ["alpha", "beta"], {"alpha": date(2024, 1, 1), "beta": date(2024, 1, 15)})
        self.assertEqual(rows[0]["beta"], "")
        self.assertEqual(rows[1]["beta"], "")
        self.assertEqual(rows[2]["beta"], 2)

    def test_complete_week_uses_last_complete_row(self):
        rows = [{"week_start": "2024-01-01"}, {"week_start": "2024-01-08"}]
        self.assertEqual(complete_week(rows, date(2024, 1, 14)), "2024-01-08")
        self.assertIsNone(complete_week(rows, date(2024, 1, 6)))

    def test_clickhouse_csv_parses_named_rows(self):
        with patch("lib.pypi_dashboard.fetch_url", return_value="week_start,project,downloads\n2024-01-01,alpha,5\n"):
            rows = clickhouse_csv("SELECT 1", user_agent="test")
        self.assertEqual(rows, [{"week_start": "2024-01-01", "project": "alpha", "downloads": "5"}])

    def test_non_404_metadata_failure_is_not_treated_as_missing(self):
        error = urllib.error.HTTPError("https://pypi.org", 503, "unavailable", {}, None)
        with patch("lib.pypi_dashboard.fetch_url", side_effect=error):
            with self.assertRaises(urllib.error.HTTPError):
                from lib.pypi_dashboard import load_meta

                load_meta("demo", user_agent="test")

    def test_write_outputs_writes_csv_and_metadata_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = PyPIConfig("demo", ["demo"], root / "data.csv", root / "metadata.json")
            rows = [{"week_start": "2024-01-01", "demo": 7}]
            metas = {"demo": PackageMeta(exists=True, first_upload=date(2024, 1, 2))}
            write_outputs(rows, metas, date(2024, 1, 7), config)
            self.assertTrue(config.csv_path.is_file())
            self.assertTrue(config.meta_path.is_file())
            metadata = json.loads(config.meta_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["dataset"]["rows"], 1)
            self.assertEqual(metadata["dataset"]["columns"], ["week_start", "demo"])


if __name__ == "__main__":
    unittest.main()

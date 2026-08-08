import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_dashboard_data import ValidationError, validate_dataset


class DashboardDataValidationTests(unittest.TestCase):
    def _write_dataset(self, root: Path, csv_text: str, **dataset_overrides):
        data_dir = root / "Data"
        metadata_dir = root / "json"
        data_dir.mkdir()
        metadata_dir.mkdir()
        csv_path = data_dir / "demo.csv"
        metadata_path = metadata_dir / "demo_metadata.json"
        csv_path.write_text(csv_text, encoding="utf-8")
        dataset = {
            "csv": "demo.csv",
            "rows": 1,
            "columns": ["week_start", "demo"],
            "latest_complete_week_start": "2024-01-01",
            **dataset_overrides,
        }
        metadata_path.write_text(json.dumps({
            "vendor": "demo",
            "source": {
                "latest_download_day": "2024-01-07",
                "latest_complete_week_start": "2024-01-01",
            },
            "dataset": dataset,
            "packages": {"demo": {"exists": True}},
        }), encoding="utf-8")
        return csv_path, metadata_path

    def test_valid_dataset_returns_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, metadata_path = self._write_dataset(Path(directory), "week_start,demo\n2024-01-01,7\n")
            summary = validate_dataset(csv_path, metadata_path)
        self.assertEqual(summary["rows"], 1)
        self.assertEqual(summary["latest_complete_week_start"], "2024-01-01")

    def test_non_monday_week_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, metadata_path = self._write_dataset(Path(directory), "week_start,demo\n2024-01-02,7\n")
            with self.assertRaisesRegex(ValidationError, "Monday"):
                validate_dataset(csv_path, metadata_path)

    def test_invalid_numeric_value_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, metadata_path = self._write_dataset(Path(directory), "week_start,demo\n2024-01-01,NaN\n")
            with self.assertRaisesRegex(ValidationError, "non-negative integer"):
                validate_dataset(csv_path, metadata_path)


if __name__ == "__main__":
    unittest.main()

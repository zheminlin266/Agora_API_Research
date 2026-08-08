import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from lib.npm_dashboard import (
    PackageMeta,
    VendorConfig,
    build_rows,
    iter_ranges,
    latest_complete_week,
    parse_iso_date,
    week_start,
    write_outputs,
)


class NpmDashboardTests(unittest.TestCase):
    def test_date_helpers(self):
        self.assertEqual(parse_iso_date("2026-08-08T12:00:00Z"), date(2026, 8, 8))
        self.assertEqual(week_start(date(2026, 8, 8)), date(2026, 8, 3))
        self.assertEqual(latest_complete_week(date(2026, 8, 8)), date(2026, 7, 27))

    def test_iter_ranges_is_contiguous_and_bounded(self):
        ranges = list(iter_ranges(date(2020, 1, 1), date(2022, 1, 1)))
        self.assertGreater(len(ranges), 1)
        self.assertEqual(ranges[0][0], date(2020, 1, 1))
        self.assertEqual(ranges[-1][1], date(2022, 1, 1))
        for previous, current in zip(ranges, ranges[1:]):
            self.assertEqual(previous[1].toordinal() + 1, current[0].toordinal())

    def test_build_rows_aligns_weekly_values(self):
        metas = {"demo": PackageMeta(exists=True, created=date(2024, 1, 2), created_raw="2024-01-02T00:00:00Z")}
        downloads = {"demo": {date(2024, 1, 1): 7}}
        rows = build_rows(metas, downloads, date(2024, 1, 14))
        self.assertEqual(rows, [{"week_start": "2024-01-01", "demo": "7"}, {"week_start": "2024-01-08", "demo": "0"}])

    def test_write_outputs_writes_csv_and_metadata_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = VendorConfig("demo", ["demo"], root / "data.csv", root / "metadata.json")
            rows = [{"week_start": "2024-01-01", "demo": "7"}]
            metas = {"demo": PackageMeta(exists=True, created=date(2024, 1, 2), created_raw="2024-01-02T00:00:00Z")}
            write_outputs(rows, metas, date(2024, 1, 7), config)
            self.assertTrue(config.csv_path.is_file())
            self.assertTrue(config.meta_path.is_file())
            metadata = json.loads(config.meta_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["dataset"]["rows"], 1)
            self.assertEqual(metadata["dataset"]["columns"], ["week_start", "demo"])


if __name__ == "__main__":
    unittest.main()

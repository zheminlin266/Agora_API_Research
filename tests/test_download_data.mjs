import assert from "node:assert/strict";

import { DownloadDataError, parseDownloadDataset } from "../lib/download-data.ts";

const csv = [
  "week_start,alpha,beta",
  "2024-01-01,5,",
  "2024-01-08,0,2",
  "",
].join("\n");

const metadata = {
  vendor: "demo",
  source: { latest_complete_week_start: "2024-01-01" },
  dataset: {
    csv: "demo.csv",
    rows: 2,
    columns: ["week_start", "alpha", "beta"],
    latest_complete_week_start: "2024-01-01",
  },
};

const parsed = parseDownloadDataset(csv, metadata, { expectedCsvFilename: "demo.csv" });
assert.deepEqual(parsed.rows, [
  { week_start: "2024-01-01", alpha: 5, beta: null },
  { week_start: "2024-01-08", alpha: 0, beta: 2 },
]);
assert.equal(parsed.completeWeek, "2024-01-01");

assert.throws(
  () => parseDownloadDataset(csv.replace(",5,", ",NaN,"), metadata, { expectedCsvFilename: "demo.csv" }),
  DownloadDataError,
);
assert.throws(
  () => parseDownloadDataset(csv, { ...metadata, dataset: { ...metadata.dataset, rows: 1 } }, { expectedCsvFilename: "demo.csv" }),
  /rows does not match/,
);
assert.throws(
  () => parseDownloadDataset(csv, { ...metadata, source: {} }, { expectedCsvFilename: "demo.csv" }),
  /latest_complete_week_start/,
);
assert.throws(
  () => parseDownloadDataset(csv.replace("2024-01-08", "2024-01-09"), metadata, { expectedCsvFilename: "demo.csv" }),
  /Monday/,
);

console.log("download-data parser checks passed");

"""Safe, locked output primitives shared by dashboard data generators."""

from __future__ import annotations

import csv
import hashlib
import math
import os
import re
import shutil
import tempfile
import time
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Mapping, Sequence


INTEGER_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")


class OutputSafetyError(RuntimeError):
    """Raised when a generated output is empty, malformed, or unexpectedly smaller."""


def _validate_value(value: object, field: str) -> None:
    if value == "":
        return
    if isinstance(value, bool):
        raise OutputSafetyError(f"{field} must be a non-negative integer or blank")
    if isinstance(value, int):
        if value < 0:
            raise OutputSafetyError(f"{field} must be a non-negative integer or blank")
        return
    if isinstance(value, str) and INTEGER_RE.fullmatch(value):
        return
    raise OutputSafetyError(f"{field} must be a non-negative integer or blank")


def validate_rows(rows: Sequence[Mapping[str, object]], columns: Sequence[str]) -> None:
    """Validate rows before they can replace a published dashboard file."""

    if not rows:
        raise OutputSafetyError("Refusing to write an empty dashboard dataset")
    if not columns or columns[0] != "week_start" or len(set(columns)) != len(columns):
        raise OutputSafetyError("Dashboard columns must be unique and start with week_start")

    previous: date | None = None
    for index, row in enumerate(rows, start=2):
        if set(row) != set(columns):
            raise OutputSafetyError(f"Row {index} columns do not match the configured schema")
        raw_week = row["week_start"]
        try:
            current = date.fromisoformat(str(raw_week))
        except ValueError as exc:
            raise OutputSafetyError(f"Row {index}.week_start is not an ISO date") from exc
        if current.weekday() != 0:
            raise OutputSafetyError(f"Row {index}.week_start is not a Monday")
        if previous is not None and current != previous + timedelta(days=7):
            raise OutputSafetyError(f"Dashboard weeks are not continuous at row {index}")
        previous = current
        for column in columns[1:]:
            _validate_value(row[column], f"Row {index}.{column}")


def load_existing_rows(csv_path: Path, columns: Sequence[str]) -> list[dict[str, str]]:
    """Load and validate a previously published CSV for an incremental refresh."""

    if not csv_path.exists():
        return []
    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(columns):
                raise OutputSafetyError(
                    f"Existing CSV columns do not match the configured schema: {csv_path}"
                )
            rows = list(reader)
    except OSError as exc:
        raise OutputSafetyError(f"Cannot read existing CSV: {csv_path}") from exc
    validate_rows(rows, columns)
    return rows


def _existing_row_count(csv_path: Path) -> int:
    if not csv_path.exists():
        return 0
    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if not header:
                raise OutputSafetyError(f"Existing CSV has no header: {csv_path}")
            return sum(1 for _ in reader)
    except OSError as exc:
            raise OutputSafetyError(f"Cannot inspect existing CSV: {csv_path}") from exc


def protect_output_shape(
    csv_path: Path,
    columns: Sequence[str],
    latest_week: date,
    new_row_count: int,
) -> None:
    """Reject schema changes or a time-range rollback over a published CSV."""

    if not csv_path.exists():
        return
    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(columns):
                raise OutputSafetyError(
                    f"Refusing to replace {csv_path.name}: dashboard columns changed"
                )
            old_latest: date | None = None
            for row in reader:
                raw_week = row.get("week_start")
                if not raw_week:
                    raise OutputSafetyError(f"Existing CSV has an invalid week_start: {csv_path}")
                old_latest = date.fromisoformat(raw_week)
    except ValueError as exc:
        raise OutputSafetyError(f"Existing CSV has an invalid week_start: {csv_path}") from exc
    except OSError as exc:
        raise OutputSafetyError(f"Cannot inspect existing CSV: {csv_path}") from exc
    if old_latest is not None and latest_week < old_latest:
        raise OutputSafetyError(
            f"Refusing to replace {csv_path.name}: latest week moved backwards "
            f"from {old_latest.isoformat()} to {latest_week.isoformat()}"
        )
    protect_row_count(csv_path, new_row_count)


def protect_row_count(csv_path: Path, new_row_count: int, minimum_ratio: float = 0.5) -> None:
    """Reject a suspiciously truncated replacement against the previous CSV."""

    old_row_count = _existing_row_count(csv_path)
    if old_row_count == 0:
        return
    minimum = max(1, math.ceil(old_row_count * minimum_ratio))
    if new_row_count < minimum:
        raise OutputSafetyError(
            f"Refusing to replace {csv_path.name}: {new_row_count} rows is below "
            f"the safety floor of {minimum} rows from the existing {old_row_count}-row file"
        )


def _lock_path_for(csv_path: Path) -> Path:
    key = str(csv_path.resolve()).lower().encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:32]
    return Path(tempfile.gettempdir()) / "agora-research-dashboard-locks" / f"{digest}.lock"


@contextmanager
def _output_lock(lock_path: Path, timeout: float = 30.0) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    acquired = False
    with lock_path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        deadline = time.monotonic() + timeout
        while not acquired:
            try:
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except (BlockingIOError, OSError) as exc:
                if time.monotonic() >= deadline:
                    raise OutputSafetyError(f"Timed out waiting for output lock: {lock_path}") from exc
                time.sleep(0.05)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _write_temp_text(directory: Path, prefix: str, text: str) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=prefix, suffix=".tmp", dir=directory)
    temp_path = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
    return temp_path


def _backup_existing(path: Path) -> Path | None:
    if not path.exists():
        return None
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.backup-", suffix=".tmp", dir=path.parent)
    os.close(descriptor)
    backup = Path(name)
    shutil.copyfile(path, backup)
    with backup.open("r+b") as handle:
        os.fsync(handle.fileno())
    return backup


def write_pair_atomic(
    csv_path: Path,
    csv_text: str,
    metadata_path: Path,
    metadata_text: str,
    *,
    columns: Sequence[str],
    latest_week: date,
    row_count: int,
) -> None:
    """Write CSV and metadata through locked temporary files with rollback."""

    if csv_path.resolve() == metadata_path.resolve():
        raise OutputSafetyError("CSV and metadata paths must be different")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = _lock_path_for(csv_path)

    with _output_lock(lock_path):
        protect_output_shape(csv_path, columns, latest_week, row_count)
        csv_temp: Path | None = None
        metadata_temp: Path | None = None
        csv_backup: Path | None = None
        metadata_backup: Path | None = None
        csv_existed = csv_path.exists()
        metadata_existed = metadata_path.exists()
        try:
            csv_temp = _write_temp_text(csv_path.parent, f".{csv_path.name}.", csv_text)
            metadata_temp = _write_temp_text(metadata_path.parent, f".{metadata_path.name}.", metadata_text)
            csv_backup = _backup_existing(csv_path)
            metadata_backup = _backup_existing(metadata_path)
            os.replace(csv_temp, csv_path)
            csv_temp = None
            os.replace(metadata_temp, metadata_path)
            metadata_temp = None
        except BaseException:
            try:
                if csv_backup is not None:
                    os.replace(csv_backup, csv_path)
                    csv_backup = None
                elif not csv_existed:
                    csv_path.unlink(missing_ok=True)
                if metadata_backup is not None:
                    os.replace(metadata_backup, metadata_path)
                    metadata_backup = None
                elif not metadata_existed:
                    metadata_path.unlink(missing_ok=True)
            finally:
                raise
        finally:
            for path in (csv_temp, metadata_temp, csv_backup, metadata_backup):
                if path is not None:
                    path.unlink(missing_ok=True)

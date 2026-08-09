"""Single source of truth for the developer-download dashboard datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .npm_dashboard import VendorConfig
from .pypi_dashboard import PyPIConfig


ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / "public" / "data" / "dev-npm-downloads"


@dataclass(frozen=True)
class DatasetSpec:
    key: str
    kind: Literal["npm", "pypi"]
    vendor: str
    registry: str
    packages: tuple[str, ...]
    csv_path: Path
    metadata_path: Path
    user_agent: str

    def config(self) -> VendorConfig | PyPIConfig:
        common = {
            "vendor": self.vendor,
            "packages": list(self.packages),
            "csv_path": self.csv_path,
            "meta_path": self.metadata_path,
            "user_agent": self.user_agent,
        }
        return VendorConfig(**common) if self.kind == "npm" else PyPIConfig(**common)


DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        key="agoraNpm",
        kind="npm",
        vendor="agora",
        registry="npm",
        packages=("agora-rtc-sdk-ng", "agora-rtm-sdk", "agora-rtc-react", "react-native-agora"),
        csv_path=DATA_ROOT / "Data" / "agora_npm_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "agora_npm_downloads_metadata.json",
        user_agent="codex-agora-npm-dashboard/2.0",
    ),
    DatasetSpec(
        key="agoraPypi",
        kind="pypi",
        vendor="agora",
        registry="PyPI",
        packages=("agora-token-builder", "agora-python-server-sdk"),
        csv_path=DATA_ROOT / "Data" / "agora_pypi_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "agora_pypi_downloads_metadata.json",
        user_agent="codex-agora-pypi-dashboard/2.0",
    ),
    DatasetSpec(
        key="livekitNpm",
        kind="npm",
        vendor="livekit",
        registry="npm",
        packages=(
            "livekit-client",
            "@livekit/components-react",
            "@livekit/react-native",
            "@livekit/agents",
            "@livekit/agents-plugin-silero",
        ),
        csv_path=DATA_ROOT / "Data" / "livekit_npm_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "livekit_npm_downloads_metadata.json",
        user_agent="codex-livekit-npm-dashboard/2.0",
    ),
    DatasetSpec(
        key="livekitPypi",
        kind="pypi",
        vendor="livekit",
        registry="PyPI",
        packages=("livekit", "livekit-api", "livekit-agents"),
        csv_path=DATA_ROOT / "Data" / "livekit_pypi_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "livekit_pypi_downloads_metadata.json",
        user_agent="codex-livekit-pypi-dashboard/2.0",
    ),
    DatasetSpec(
        key="twilioNpm",
        kind="npm",
        vendor="twilio",
        registry="npm",
        packages=("@twilio/voice-sdk", "twilio"),
        csv_path=DATA_ROOT / "Data" / "twilio_npm_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "twilio_npm_downloads_metadata.json",
        user_agent="codex-twilio-npm-dashboard/2.0",
    ),
    DatasetSpec(
        key="rtcNpm",
        kind="npm",
        vendor="tencent",
        registry="npm",
        packages=("trtc-cloud-js-sdk",),
        csv_path=DATA_ROOT / "Data" / "rtc_competitor_npm_weekly_downloads.csv",
        metadata_path=DATA_ROOT / "json" / "rtc_competitor_npm_downloads_metadata.json",
        user_agent="codex-rtc-competitor-dashboard/2.0",
    ),
)


def manifest_payload() -> dict[str, object]:
    """Return the frontend data contract derived from the dataset registry."""

    datasets: dict[str, object] = {}
    packages: list[dict[str, str]] = []
    for spec in DATASETS:
        datasets[spec.key] = {
            "vendor": spec.vendor,
            "registry": spec.registry,
            "csv": spec.csv_path.relative_to(DATA_ROOT).as_posix(),
            "metadata": spec.metadata_path.relative_to(DATA_ROOT).as_posix(),
            "packages": list(spec.packages),
        }
        packages.extend(
            {"vendor": spec.vendor, "dataset": spec.key, "key": package}
            for package in spec.packages
        )
    return {
        "version": 1,
        "data_root": "/data/dev-npm-downloads",
        "datasets": datasets,
        "packages": packages,
    }

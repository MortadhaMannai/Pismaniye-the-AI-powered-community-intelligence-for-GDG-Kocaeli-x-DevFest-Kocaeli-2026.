"""Environment configuration and runtime settings for PISMANIYE."""

from __future__ import annotations

from pathlib import Path
import secrets
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PismaniyeSettings(BaseSettings):
    """Global settings supporting both Google Cloud production and deterministic local mode."""

    model_config = SettingsConfigDict(
        env_prefix="PISMANIYE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Event Edition Metadata
    event_id: str = Field(
        default="devfest-kocaeli-2026",
        description="Active event identifier (reusable for devfest-kocaeli-2027, etc.)",
    )
    event_name: str = Field(default="DevFest Kocaeli 2026")
    community_name: str = Field(default="GDG Kocaeli")
    tagline: str = Field(default="Unraveling People. Connecting Possibilities.")

    # Runtime Mode
    mode: Literal["local_deterministic", "google_cloud", "hybrid"] = Field(
        default="local_deterministic",
        description="Execution mode. Works deterministically offline without API keys by default.",
    )
    deterministic_seed: int = Field(default=2026)

    # Google Cloud & GenAI Settings
    google_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY", repr=False)
    gcp_project_id: str | None = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    gcp_location: str = Field(default="europe-west1", alias="GOOGLE_CLOUD_LOCATION")
    gemini_model: str = Field(default="gemini-2.5-flash")
    embedding_model: str = Field(default="text-embedding-004")
    firestore_collection_prefix: str = Field(default="pismaniye_devfest2026")
    gcs_bucket_name: str | None = Field(default=None)

    # Storage & Local Persistence
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent / ".pismaniye_state",
        description="Local state directory for persistence, traces, and audit logs.",
    )

    # Server & Web App Settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)
    public_web_url: str = Field(
        default="https://pismaniye-concierge.gdgkocaeli.dev",
        description="Public Web App URL encoded in stage/terminal QR codes (configurable via PISMANIYE_PUBLIC_WEB_URL).",
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["https://pismaniye-concierge.gdgkocaeli.dev"]
    )
    organizer_passcode: str = Field(
        default_factory=lambda: secrets.token_urlsafe(18),
        repr=False,
        description="Ephemeral or env-configured RBAC passcode for organizer mutations (never hardcoded).",
    )

    # Privacy & Governance
    require_explicit_opt_in: bool = Field(default=True)
    require_intro_consent: bool = Field(default=True)
    data_retention_days: int = Field(default=90)
    enable_otel_tracing: bool = Field(default=True)

    @property
    def has_gemini_credentials(self) -> bool:
        return bool(self.google_api_key or (self.gcp_project_id and self.mode != "local_deterministic"))

    def ensure_dirs(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "traces").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "decisions").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "reports").mkdir(parents=True, exist_ok=True)
        return self.data_dir


_settings: PismaniyeSettings | None = None


def get_settings() -> PismaniyeSettings:
    global _settings
    if _settings is None:
        _settings = PismaniyeSettings()
        _settings.ensure_dirs()
    return _settings


def reload_settings(**overrides: object) -> PismaniyeSettings:
    global _settings
    _settings = PismaniyeSettings(**overrides)  # type: ignore[arg-type]
    _settings.ensure_dirs()
    return _settings

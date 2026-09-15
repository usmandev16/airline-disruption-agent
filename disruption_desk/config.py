"""Loads and validates configuration from .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

_REQUIRED = ("OPS_BASE_URL", "OPS_API_KEY")


_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_AUTONOMY_LIMIT_GBP = 300.0
_DEFAULT_CUMULATIVE_LIMIT_GBP = 500.0

# gpt-4o-mini's published per-1M-token rates (USD). Override via env if you point at a
# different model/provider so the printed cost estimate stays meaningful.
_DEFAULT_INPUT_PRICE_PER_1M_USD = 0.15
_DEFAULT_OUTPUT_PRICE_PER_1M_USD = 0.60


def _float_env(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        raise RuntimeError(f"{name} must be a number, got {raw!r}.")


@dataclass(frozen=True)
class Config:
    ops_base_url: str
    ops_api_key: str
    openai_api_key: Optional[str]
    openai_base_url: Optional[str]
    openai_model: str
    autonomy_limit_gbp: float
    cumulative_limit_gbp: float
    input_price_per_1m_usd: float
    output_price_per_1m_usd: float

    def require_openai_key(self) -> str:
        """Fail loudly, but only when something actually needs the OpenAI key."""
        if not self.openai_api_key:
            raise RuntimeError(
                "Missing required environment variable: OPENAI_API_KEY. "
                "Set it in .env before making OpenAI calls."
            )
        return self.openai_api_key


def load_config() -> Config:
    values = {name: os.environ.get(name, "").strip() for name in _REQUIRED}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            f"{', '.join(missing)}. Copy .env.example to .env and fill them in."
        )
    return Config(
        ops_base_url=values["OPS_BASE_URL"].rstrip("/"),
        ops_api_key=values["OPS_API_KEY"],
        openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip() or None,
        openai_base_url=os.environ.get("OPENAI_BASE_URL", "").strip() or None,
        openai_model=os.environ.get("OPENAI_MODEL", "").strip() or _DEFAULT_MODEL,
        autonomy_limit_gbp=_float_env("AUTONOMY_LIMIT_GBP", _DEFAULT_AUTONOMY_LIMIT_GBP),
        cumulative_limit_gbp=_float_env("CUMULATIVE_LIMIT_GBP", _DEFAULT_CUMULATIVE_LIMIT_GBP),
        input_price_per_1m_usd=_float_env("OPENAI_INPUT_PRICE_PER_1M_USD", _DEFAULT_INPUT_PRICE_PER_1M_USD),
        output_price_per_1m_usd=_float_env("OPENAI_OUTPUT_PRICE_PER_1M_USD", _DEFAULT_OUTPUT_PRICE_PER_1M_USD),
    )

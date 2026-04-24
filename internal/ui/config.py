import os
from pathlib import Path

from dotenv import load_dotenv

# Load from internal/.env (parent of playwright/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required config: {key}. Check your .env file.")
    return value


# Cortex web UI
BASE_URL = get("CORTEX_APP_URL", "https://app.getcortexapp.com")
TENANT_CODE = get("CORTEX_TENANT_CODE")

# Cortex API (for test setup/teardown)
API_BASE_URL = get("CORTEX_BASE_URL", "https://api.getcortexapp.com")
API_KEY = get("CORTEX_API_KEY")

# Google auth
GOOGLE_EMAIL = get("GOOGLE_EMAIL")
GOOGLE_PASSWORD = get("GOOGLE_PASSWORD")
GOOGLE_TOTP_URI = get("GOOGLE_TOTP_URI")

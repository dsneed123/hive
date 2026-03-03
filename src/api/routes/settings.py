import os
from pathlib import Path
from fastapi import APIRouter
from src.api.models.schemas import SettingsData, SettingsResponse

router = APIRouter()

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def _read_env() -> dict[str, str]:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _write_env(env: dict[str, str]):
    lines = [f'{k}="{v}"' for k, v in env.items()]
    ENV_PATH.write_text("\n".join(lines) + "\n")


@router.get("/settings", response_model=SettingsResponse)
async def get_settings():
    settings = SettingsData(
        claude_key=os.getenv("CLAUDE_KEY", ""),
        gmail_address=os.getenv("GMAIL_ADDRESS", ""),
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
    )
    return SettingsResponse(settings=settings)


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(data: SettingsData):
    env = _read_env()

    if data.claude_key:
        env["CLAUDE_KEY"] = data.claude_key
        os.environ["CLAUDE_KEY"] = data.claude_key
    if data.gmail_address is not None:
        env["GMAIL_ADDRESS"] = data.gmail_address
        os.environ["GMAIL_ADDRESS"] = data.gmail_address
    if data.gmail_app_password is not None:
        env["GMAIL_APP_PASSWORD"] = data.gmail_app_password
        os.environ["GMAIL_APP_PASSWORD"] = data.gmail_app_password

    _write_env(env)

    settings = SettingsData(
        claude_key=os.getenv("CLAUDE_KEY", ""),
        gmail_address=os.getenv("GMAIL_ADDRESS", ""),
        gmail_app_password=os.getenv("GMAIL_APP_PASSWORD", ""),
    )
    return SettingsResponse(settings=settings, message="Settings saved successfully")

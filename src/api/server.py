from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import chat, analytics, settings, calendar, history, accounts, emails
from src.database import init_db

app = FastAPI(title="Hive API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(calendar.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(emails.router, prefix="/api")


@app.on_event("startup")
def startup():
    import os
    from src.database import get_accounts, add_account
    init_db()
    # Migrate: seed existing env TikTok account into DB if no accounts exist
    if not get_accounts():
        username = os.getenv("TIKTOK_USERNAME", "")
        url = os.getenv("TIKTOK_URL", "")
        if username and url:
            add_account(username, url)


@app.get("/api/health")
async def health():
    return {"status": "ok"}

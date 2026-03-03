import os
from fastapi import APIRouter, HTTPException
from src.api.models.schemas import ChatRequest, ChatResponse
from src.Chat_Mode import claude_chat
from src.analytics import get_tiktok_analytics, parse_tiktok_profile
from src.database import get_active_account

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    api_key = os.getenv("CLAUDE_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="CLAUDE_KEY not configured")

    account = get_active_account()
    tiktok_username = account["username"] if account else ""
    tiktok_url = account["tiktok_url"] if account else ""

    # Fetch and parse TikTok data (pass structured data, not raw HTML)
    account_data = {}
    if tiktok_url:
        try:
            html = get_tiktok_analytics(tiktok_url)
            account_data = parse_tiktok_profile(html)
        except Exception:
            account_data = {}

    history = [{"role": m.role, "content": m.content} for m in request.history]

    try:
        response_text = claude_chat(
            api_key=api_key,
            message=request.message,
            tiktok_username=tiktok_username,
            account_data=account_data,
            history=history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(response=response_text)

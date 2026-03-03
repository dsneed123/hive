from fastapi import APIRouter, HTTPException
from src.api.models.schemas import AnalyticsResponse
from src.analytics import get_tiktok_analytics, parse_tiktok_profile
from src.database import save_snapshot, get_active_account

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
async def analytics():
    account = get_active_account()
    if not account:
        raise HTTPException(status_code=400, detail="No active TikTok account. Add one in Settings.")

    tiktok_url = account["tiktok_url"]

    try:
        html = get_tiktok_analytics(tiktok_url)
        profile = parse_tiktok_profile(html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save snapshot for historical tracking (rate-limited to 1 per hour)
    try:
        save_snapshot(profile)
    except Exception:
        pass  # Don't fail the request if snapshot save fails

    return AnalyticsResponse(**profile)

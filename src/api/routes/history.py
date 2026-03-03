from fastapi import APIRouter
from src.api.models.schemas import AnalyticsHistoryResponse
from src.database import get_snapshots, get_active_account

router = APIRouter()


@router.get("/analytics/history", response_model=AnalyticsHistoryResponse)
async def analytics_history(days: int = 30):
    account = get_active_account()
    username = account["username"] if account else ""
    snapshots = get_snapshots(username=username, days=days)
    return AnalyticsHistoryResponse(snapshots=snapshots)

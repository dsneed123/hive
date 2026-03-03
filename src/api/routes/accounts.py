from fastapi import APIRouter, HTTPException
from src.api.models.schemas import AccountCreate, AccountResponse, AccountsListResponse
from src.database import add_account, get_accounts, get_active_account, set_active_account, remove_account

router = APIRouter()


@router.get("/accounts", response_model=AccountsListResponse)
async def list_accounts():
    accounts = get_accounts()
    return AccountsListResponse(accounts=accounts)


@router.post("/accounts", response_model=AccountResponse)
async def create_account(data: AccountCreate):
    if not data.username or not data.tiktok_url:
        raise HTTPException(status_code=400, detail="Username and TikTok URL are required")
    account = add_account(data.username, data.tiktok_url)
    return AccountResponse(**account)


@router.put("/accounts/{account_id}/activate", response_model=AccountResponse)
async def activate_account(account_id: int):
    account = set_active_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountResponse(**account)


@router.delete("/accounts/{account_id}")
async def delete_account(account_id: int):
    deleted = remove_account(account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account removed"}

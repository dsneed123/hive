import os
from fastapi import APIRouter, HTTPException
from src.api.models.schemas import (
    EmailResponse, EmailListResponse, EmailDraftRequest,
    EmailModeResponse, EmailModeUpdate, EmailSendRequest,
)
from src.database import (
    save_emails, get_emails, get_email, update_email_draft,
    get_email_mode, set_email_mode, get_active_account,
    mark_email_replied, get_replied_message_ids, mark_replied_by_message_id,
)
from src.email_manager import fetch_emails, send_email, check_sent_for_replies
from src.Chat_Mode import draft_email_reply

router = APIRouter()


@router.get("/emails", response_model=EmailListResponse)
async def list_emails(category: str = "", page: int = 1):
    emails = get_emails(category=category, page=page)
    return EmailListResponse(emails=emails, page=page)


@router.get("/emails/mode", response_model=EmailModeResponse)
async def get_mode():
    mode = get_email_mode()
    return EmailModeResponse(mode=mode)


@router.put("/emails/mode", response_model=EmailModeResponse)
async def update_mode(data: EmailModeUpdate):
    if data.mode not in ("test", "reply"):
        raise HTTPException(status_code=400, detail="Mode must be 'test' or 'reply'")
    mode = set_email_mode(data.mode)
    return EmailModeResponse(mode=mode)


@router.get("/emails/{email_id}", response_model=EmailResponse)
async def get_single_email(email_id: int):
    email_data = get_email(email_id)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")
    return EmailResponse(**email_data)


@router.post("/emails/fetch")
async def trigger_fetch():
    gmail_address = os.getenv("GMAIL_ADDRESS", "")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "")
    if not gmail_address or not gmail_app_password:
        raise HTTPException(status_code=400, detail="Gmail credentials not configured")

    try:
        emails_list = fetch_emails(
            gmail_address=gmail_address,
            gmail_app_password=gmail_app_password,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

    count = save_emails(emails_list)

    # Check Sent folder for replies to known collaboration emails
    collab_emails = get_emails(category="collaboration", page=1, per_page=500)
    already_replied = get_replied_message_ids()
    unreplied_ids = {e["message_id"] for e in collab_emails if e["message_id"] not in already_replied}
    if unreplied_ids:
        replied_ids = check_sent_for_replies(
            gmail_address=gmail_address,
            gmail_app_password=gmail_app_password,
            known_message_ids=unreplied_ids,
        )
        for mid in replied_ids:
            mark_replied_by_message_id(mid)

    return {"message": f"Fetched {len(emails_list)} emails, {count} new saved"}


@router.post("/emails/{email_id}/draft", response_model=EmailResponse)
async def generate_draft(email_id: int, data: EmailDraftRequest):
    email_data = get_email(email_id)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")

    api_key = os.getenv("CLAUDE_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    account = get_active_account()
    mode = get_email_mode()

    try:
        draft = draft_email_reply(
            api_key=api_key,
            email_data=email_data,
            account_context=account,
            instructions=data.instructions,
            mode=mode,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")

    updated = update_email_draft(email_id, draft)
    return EmailResponse(**updated)


@router.post("/emails/{email_id}/send")
async def send_reply(email_id: int, data: EmailSendRequest):
    mode = get_email_mode()
    if mode != "reply":
        raise HTTPException(status_code=403, detail="Sending is disabled in test mode")

    email_data = get_email(email_id)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")

    body = data.body or email_data.get("ai_draft", "")
    if not body:
        raise HTTPException(status_code=400, detail="No reply body to send")

    # Extract sender email address
    sender = email_data.get("sender", "")
    # Handle "Name <email@example.com>" format
    if "<" in sender and ">" in sender:
        to_address = sender.split("<")[1].split(">")[0]
    else:
        to_address = sender

    subject = f"Re: {email_data.get('subject', '')}"

    try:
        send_email(to=to_address, subject=subject, body=body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send: {str(e)}")

    mark_email_replied(email_id)
    return {"message": "Reply sent successfully"}

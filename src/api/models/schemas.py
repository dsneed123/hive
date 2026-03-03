from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str


class AnalyticsResponse(BaseModel):
    username: str = ""
    nickname: str = ""
    bio: str = ""
    followers: int = 0
    following: int = 0
    likes: int = 0
    videos: int = 0
    verified: bool = False
    avatar_url: str = ""


class SettingsData(BaseModel):
    claude_key: str = ""
    gmail_address: str = ""
    gmail_app_password: str = ""


class SettingsResponse(BaseModel):
    settings: SettingsData
    message: str = ""


# --- Accounts ---

class AccountCreate(BaseModel):
    username: str
    tiktok_url: str


class AccountResponse(BaseModel):
    id: int
    username: str
    tiktok_url: str
    is_active: bool = False
    created_at: str = ""


class AccountsListResponse(BaseModel):
    accounts: list[AccountResponse] = []


# --- Calendar ---

class CalendarEventCreate(BaseModel):
    title: str
    description: str = ""
    date: str  # YYYY-MM-DD
    time: str = ""  # HH:MM
    event_type: str = "note"  # post, idea, note


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    event_type: Optional[str] = None


class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str = ""
    date: str
    time: str = ""
    event_type: str = "note"
    created_at: str = ""
    updated_at: str = ""


class CalendarEventsListResponse(BaseModel):
    events: list[CalendarEventResponse] = []


# --- Analytics History ---

class AnalyticsSnapshot(BaseModel):
    id: int
    timestamp: str
    username: str = ""
    nickname: str = ""
    followers: int = 0
    following: int = 0
    likes: int = 0
    videos: int = 0


class AnalyticsHistoryResponse(BaseModel):
    snapshots: list[AnalyticsSnapshot] = []


# --- Emails ---

class EmailResponse(BaseModel):
    id: int
    message_id: str = ""
    sender: str = ""
    subject: str = ""
    body_preview: str = ""
    category: str = "other"
    is_read: bool = False
    replied: bool = False
    ai_draft: str = ""
    received_at: str = ""
    fetched_at: str = ""


class EmailListResponse(BaseModel):
    emails: list[EmailResponse] = []
    page: int = 1


class EmailDraftRequest(BaseModel):
    instructions: str = ""


class EmailModeResponse(BaseModel):
    mode: str = "test"


class EmailModeUpdate(BaseModel):
    mode: str  # "test" or "reply"


class EmailSendRequest(BaseModel):
    body: str = ""

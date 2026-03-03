import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime
import os
import re


# Keywords that indicate TikTok video collaboration outreach
COLLAB_KEYWORDS = [
    "tiktok video", "tiktok collab", "tiktok collaboration", "tiktok campaign",
    "tiktok creator", "tiktok content", "tiktok post", "tiktok partnership",
    "tiktok sponsor", "tiktok ambassador", "tiktok promotion",
]

# Broader outreach keywords — only count as collab if paired with a TikTok mention
OUTREACH_KEYWORDS = [
    "collab", "collaboration", "partnership", "sponsor", "brand deal",
    "paid", "campaign", "ambassador", "creator program",
    "gifting", "pr package", "media kit", "brand partnership",
    "content creator", "sponsored post", "sponsored content",
    "product review", "affiliate", "ugc", "user generated content",
    "product seeding", "compensation", "deliverables", "rate card",
    "would love to work with you", "love your content", "love your work",
    "interested in working", "reach out to you", "reaching out",
    "on behalf of", "marketing team", "talent manager",
]

# TikTok platform indicators
TIKTOK_MENTIONS = [
    "tiktok", "tik tok", "@dsneedy", "dsneedy",
]

PROMO_KEYWORDS = [
    "sale", "discount", "offer", "promo", "deal", "coupon",
    "limited time", "% off", "free trial", "subscribe", "unsubscribe",
]

SPAM_PATTERNS = [
    "nigerian", "lottery", "winner", "claim your prize", "click here now",
    "act now", "urgent", "verify your account", "suspended",
    "no-reply@", "noreply@", "mailer-daemon",
]


def _decode_header_value(value: str) -> str:
    if not value:
        return ""
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        # Fallback to HTML if no plain text
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html = payload.decode(charset, errors="replace")
                    # Strip HTML tags for preview
                    return re.sub(r"<[^>]+>", " ", html).strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def classify_email(subject: str, sender: str, body: str) -> str:
    text = f"{subject} {sender} {body}".lower()

    for pattern in SPAM_PATTERNS:
        if pattern in text:
            return "spam"

    # Check for TikTok video collaboration specifically
    # Direct TikTok collab phrases are an instant match
    collab_score = sum(1 for kw in COLLAB_KEYWORDS if kw in text)

    # General outreach keywords only count if TikTok is mentioned
    mentions_tiktok = any(t in text for t in TIKTOK_MENTIONS)
    if mentions_tiktok:
        collab_score += sum(1 for kw in OUTREACH_KEYWORDS if kw in text)

    promo_score = sum(1 for kw in PROMO_KEYWORDS if kw in text)

    if collab_score > 0 and collab_score >= promo_score:
        return "collaboration"

    if promo_score > 0:
        return "promotion"

    return "other"


def connect_imap(gmail_address: str = "", gmail_app_password: str = ""):
    address = gmail_address or os.getenv("GMAIL_ADDRESS", "")
    password = gmail_app_password or os.getenv("GMAIL_APP_PASSWORD", "")
    if not address or not password:
        raise ValueError("Gmail credentials not configured")

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(address, password)
    return imap


def fetch_emails(folder: str = "INBOX", limit: int = 50,
                 gmail_address: str = "", gmail_app_password: str = "") -> list[dict]:
    imap = connect_imap(gmail_address, gmail_app_password)
    imap.select(folder, readonly=True)

    _, message_numbers = imap.search(None, "ALL")
    nums = message_numbers[0].split()

    # Get the most recent `limit` emails
    nums = nums[-limit:] if len(nums) > limit else nums
    nums.reverse()  # newest first

    emails_list = []
    for num in nums:
        _, msg_data = imap.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                message_id = msg.get("Message-ID", f"unknown-{num.decode()}")
                sender = _decode_header_value(msg.get("From", ""))
                subject = _decode_header_value(msg.get("Subject", ""))
                body = _get_body(msg)
                body_preview = body[:500] if body else ""

                # Parse date
                date_str = msg.get("Date", "")
                try:
                    received_at = parsedate_to_datetime(date_str).isoformat()
                except Exception:
                    received_at = datetime.utcnow().isoformat()

                category = classify_email(subject, sender, body_preview)

                emails_list.append({
                    "message_id": message_id,
                    "sender": sender,
                    "subject": subject,
                    "body_preview": body_preview,
                    "category": category,
                    "received_at": received_at,
                })

    imap.logout()
    return emails_list


def check_sent_for_replies(gmail_address: str = "", gmail_app_password: str = "",
                           known_message_ids: set[str] = None) -> set[str]:
    """Check the Sent folder for replies to known emails.
    Returns a set of original message_ids that have been replied to."""
    if not known_message_ids:
        return set()
    replied_ids = set()
    try:
        imap = connect_imap(gmail_address, gmail_app_password)
        imap.select('"[Gmail]/Sent Mail"', readonly=True)
        _, message_numbers = imap.search(None, "ALL")
        nums = message_numbers[0].split()
        # Only check the last 200 sent emails for performance
        nums = nums[-200:] if len(nums) > 200 else nums
        for num in nums:
            _, msg_data = imap.fetch(num, "(BODY.PEEK[HEADER.FIELDS (IN-REPLY-TO REFERENCES)])")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    header_text = response_part[1].decode("utf-8", errors="replace")
                    for mid in known_message_ids:
                        if mid in header_text:
                            replied_ids.add(mid)
        imap.logout()
    except Exception:
        pass
    return replied_ids


def send_email(to: str, subject: str, body: str,
               gmail_address: str = "", gmail_app_password: str = ""):
    address = gmail_address or os.getenv("GMAIL_ADDRESS", "")
    password = gmail_app_password or os.getenv("GMAIL_APP_PASSWORD", "")
    if not address or not password:
        raise ValueError("Gmail credentials not configured")

    msg = MIMEMultipart()
    msg["From"] = address
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(address, password)
        server.send_message(msg)

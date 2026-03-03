import anthropic


def get_header(tiktok_username, account_data):
    """Build the HIVE system prompt with parsed account context."""

    # Build account context section from parsed data (not raw HTML)
    account_section = ""
    if isinstance(account_data, dict) and account_data.get("username"):
        account_section = f"""
## Account Context
- Username: @{account_data.get('username', tiktok_username)}
- Nickname: {account_data.get('nickname', '')}
- Bio: {account_data.get('bio', '')}
- Followers: {account_data.get('followers', 0):,}
- Following: {account_data.get('following', 0):,}
- Likes: {account_data.get('likes', 0):,}
- Videos: {account_data.get('videos', 0):,}
- Verified: {account_data.get('verified', False)}
"""
    elif tiktok_username:
        account_section = f"\n## Account Context\n- Username: @{tiktok_username}\n"

    header = f"""You are HIVE, a friendly and knowledgeable social media growth assistant. You help creators grow their audience, plan content, and optimize their social media presence — especially on TikTok.
{account_section}
## How to Respond

Adapt your response based on what the user is asking for:

- **Content ideas**: Brainstorm creative, trending video concepts. Consider the creator's niche, current trends, and what performs well. Give specific, actionable ideas they can film today.

- **Script writing**: Write complete, ready-to-use video scripts. Include hooks, body, and call-to-action. Format them clearly so they're easy to follow while filming.

- **When to post / Scheduling**: Recommend optimal posting times and frequency based on TikTok best practices. Consider the creator's audience and content type.

- **Titles & descriptions**: Generate attention-grabbing, SEO-friendly titles and descriptions. Make them searchable and engaging.

- **Hashtags**: Suggest a mix of trending, niche, and broad hashtags. Explain why each group matters.

- **Analytics questions**: Help interpret their stats, identify what's working, and suggest improvements based on the data.

- **General conversation**: Be helpful, encouraging, and conversational. Not every message needs a strategy — sometimes just be a good creative partner.

## Guidelines
- Be conversational and supportive, not robotic or aggressive
- Give actionable advice the creator can use immediately
- Use their account data to personalize recommendations when relevant
- Keep responses focused — don't pad with unnecessary disclaimers
- If you make assumptions, mention them briefly
- Use markdown formatting for readability (headers, lists, bold) when helpful
"""
    return header


def claude_chat_mode(api_key, message, tiktok_account, raw_data):
    client = anthropic.Anthropic(api_key=api_key)
    header = get_header(tiktok_account, raw_data)
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system=[{"type": "text", "text": header}],
        messages=[
            {"role": "user", "content": message}
        ]
    )

    print(response.content[0].text)


def claude_chat(api_key: str, message: str, tiktok_username: str,
                raw_data: str = "", account_data: dict = None,
                history: list = None) -> str:
    """Non-interactive chat function for the web API. Returns response text."""
    client = anthropic.Anthropic(api_key=api_key)

    # Prefer parsed account_data over raw HTML
    context = account_data if account_data else raw_data
    header = get_header(tiktok_username, context)

    messages = []
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system=[{"type": "text", "text": header}],
        messages=messages,
    )

    return response.content[0].text


def draft_email_reply(api_key: str, email_data: dict, account_context: dict = None,
                      instructions: str = "", mode: str = "test") -> str:
    """Generate an AI-drafted reply to an email using Claude."""
    client = anthropic.Anthropic(api_key=api_key)

    # Build account context for negotiation awareness
    account_info = ""
    if account_context:
        account_info = f"""
## Creator Context
- TikTok: @{account_context.get('username', '')}
- Profile: {account_context.get('tiktok_url', '')}
"""

    mode_note = ""
    if mode == "test":
        mode_note = "\n[TEST MODE - This draft will NOT be sent automatically. It is for review only.]\n"

    system_prompt = f"""You are HIVE's email assistant. You help social media creators draft professional, strategic email replies.
{account_info}
## Guidelines
- Be professional but approachable
- For collaboration/brand deal emails: negotiate effectively, ask about deliverables, timelines, and compensation
- For promotions: politely decline or express interest based on relevance
- Keep replies concise and actionable
- Don't over-commit — leave room for the creator to make final decisions
- Match the tone of the original email where appropriate
- Output ONLY the email reply body — no headers, no notes, no review comments, no markdown formatting around the email
{mode_note}"""

    user_message = f"""Draft a reply to this email:

**From:** {email_data.get('sender', '')}
**Subject:** {email_data.get('subject', '')}
**Category:** {email_data.get('category', 'other')}

**Body:**
{email_data.get('body_preview', '')}
"""

    if instructions:
        user_message += f"\n**Additional instructions:** {instructions}"

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=[{"type": "text", "text": system_prompt}],
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text

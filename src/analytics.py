import requests
def get_tiktok_analytics(url):
   

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
  
    return response.text


def parse_tiktok_profile(html: str) -> dict:
    """Extract profile data from TikTok HTML page."""
    from bs4 import BeautifulSoup
    import json
    import re

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "username": "",
        "nickname": "",
        "bio": "",
        "followers": 0,
        "following": 0,
        "likes": 0,
        "videos": 0,
        "verified": False,
        "avatar_url": "",
    }

    # Try to extract from JSON-LD / SIGI_STATE script
    for script in soup.find_all("script", {"id": "SIGI_STATE"}):
        try:
            state = json.loads(script.string)
            user_module = state.get("UserModule", {})
            users = user_module.get("users", {})
            stats = user_module.get("stats", {})
            if users:
                uid = next(iter(users))
                u = users[uid]
                s = stats.get(uid, {})
                data["username"] = u.get("uniqueId", "")
                data["nickname"] = u.get("nickname", "")
                data["bio"] = u.get("signature", "")
                data["verified"] = u.get("verified", False)
                data["avatar_url"] = u.get("avatarLarger", "")
                data["followers"] = s.get("followerCount", 0)
                data["following"] = s.get("followingCount", 0)
                data["likes"] = s.get("heartCount", 0)
                data["videos"] = s.get("videoCount", 0)
                return data
        except (json.JSONDecodeError, StopIteration):
            pass

    # Fallback: try __UNIVERSAL_DATA_FOR_REHYDRATION__
    for script in soup.find_all("script", {"id": "__UNIVERSAL_DATA_FOR_REHYDRATION__"}):
        try:
            state = json.loads(script.string)
            user_info = (
                state.get("__DEFAULT_SCOPE__", {})
                .get("webapp.user-detail", {})
                .get("userInfo", {})
            )
            u = user_info.get("user", {})
            s = user_info.get("stats", {})
            if u:
                data["username"] = u.get("uniqueId", "")
                data["nickname"] = u.get("nickname", "")
                data["bio"] = u.get("signature", "")
                data["verified"] = u.get("verified", False)
                data["avatar_url"] = u.get("avatarLarger", "")
                data["followers"] = s.get("followerCount", 0)
                data["following"] = s.get("followingCount", 0)
                data["likes"] = s.get("heartCount", 0)
                data["videos"] = s.get("videoCount", 0)
                return data
        except (json.JSONDecodeError, StopIteration):
            pass

    # Fallback: scrape meta tags
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        data["nickname"] = title_tag.string.split("(")[0].strip()
        match = re.search(r"\(@(\w+)\)", title_tag.string)
        if match:
            data["username"] = match.group(1)

    og_desc = soup.find("meta", {"property": "og:description"})
    if og_desc:
        content = og_desc.get("content", "")
        nums = re.findall(r"([\d.]+[KMB]?)", content)
        multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
        parsed = []
        for n in nums[:3]:
            suffix = n[-1] if n[-1] in multipliers else ""
            val = float(n[:-1]) if suffix else float(n)
            parsed.append(int(val * multipliers.get(suffix, 1)))
        if len(parsed) >= 3:
            data["followers"] = parsed[0]
            data["likes"] = parsed[1]
            data["videos"] = parsed[2]

    return data
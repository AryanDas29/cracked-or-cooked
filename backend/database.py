import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

_url = os.getenv("SUPABASE_URL")
_key = os.getenv("SUPABASE_KEY")
supabase = create_client(_url, _key)

_ALIASES = {
    "cal":      "UC Berkeley",
    "berkeley": "UC Berkeley",
    "mit":      "MIT",
    "cmu":      "Carnegie Mellon",
}

def normalize_school(school: str) -> str | None:
    if not school:
        return None
    school = school.strip()
    if not school:
        return None
    lower = school.lower()
    if lower in _ALIASES:
        return _ALIASES[lower]
    return school.title()


def save_scan(data: dict):
    """Insert a scan row into the scans table."""
    row = {
        "username":        data.get("username"),
        "school":          normalize_school(data.get("school")),
        "score":           data.get("score"),
        "verdict":         data.get("verdict"),
        "ai_quality_score": data.get("ai_quality_score"),
        "public_repos":    data.get("public_repos"),
        "total_stars":     data.get("total_stars"),
        "followers":       data.get("followers"),
        "easy_solved":     data.get("easy_solved"),
        "medium_solved":   data.get("medium_solved"),
        "hard_solved":     data.get("hard_solved"),
    }
    try:
        supabase.table("scans").insert(row).execute()
    except Exception as e:
        print(f"[db] save_scan error: {e}")


def _fetch_all_deduped(school: str = None) -> list:
    """Fetch all scans, deduplicate by keeping highest score per username."""
    query = (
        supabase.table("scans")
        .select("username, school, score, verdict, ai_quality_score")
        .order("score", desc=True)
    )
    if school:
        query = query.ilike("school", f"%{school}%")
    result = query.execute()
    rows = result.data or []

    seen = set()
    deduped = []
    for row in rows:
        uname = (row.get("username") or "").lower()
        if uname not in seen:
            seen.add(uname)
            deduped.append(row)
    return deduped


def get_leaderboard(school: str = None, limit: int = 50) -> list:
    """Return top scans ordered by score desc, deduplicated by username, optionally filtered by school."""
    try:
        return _fetch_all_deduped(school)[:limit]
    except Exception as e:
        print(f"[db] get_leaderboard error: {e}")
        return []


def get_user_rank(username: str) -> dict | None:
    """Return a user's best scan entry and their global rank (1-indexed)."""
    try:
        deduped = _fetch_all_deduped()
        target = username.lower()
        for rank, row in enumerate(deduped, 1):
            if (row.get("username") or "").lower() == target:
                return {"rank": rank, **row}
        return None
    except Exception as e:
        print(f"[db] get_user_rank error: {e}")
        return None

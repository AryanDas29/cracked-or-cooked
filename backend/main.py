from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from github_fetcher import get_github_stats
from leetcode_fetcher import get_leetcode_stats
from scorer import calculate_score, get_verdict
from analyzer import analyze_github

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/compare")
async def compare(
    user1: str, user2: str,
    lc1: str = None, lc2: str = None,
):
    import asyncio
    gh1, gh2, ai1, ai2 = await asyncio.gather(
        get_github_stats(user1), get_github_stats(user2),
        analyze_github(user1), analyze_github(user2),
    )
    lc_stats1, lc_stats2 = await asyncio.gather(
        get_leetcode_stats(lc1 or user1), get_leetcode_stats(lc2 or user2)
    )

    if "error" in gh1: return {"error": gh1["error"]}
    if "error" in gh2: return {"error": gh2["error"]}

    if "error" in lc_stats1: lc_stats1 = {"easy_solved": 0, "medium_solved": 0, "hard_solved": 0, "ranking": 999999}
    if "error" in lc_stats2: lc_stats2 = {"easy_solved": 0, "medium_solved": 0, "hard_solved": 0, "ranking": 999999}

    u1 = {**gh1, **lc_stats1}
    u2 = {**gh2, **lc_stats2}

    score1 = calculate_score(u1)
    score2 = calculate_score(u2)

    return {
        "user1": {**u1, "score": score1, "verdict": get_verdict(score1), "ai_analysis": ai1},
        "user2": {**u2, "score": score2, "verdict": get_verdict(score2), "ai_analysis": ai2},
        "winner": user1 if score1 > score2 else user2,
        "winner_verdict": "CRACKED 🔥" if max(score1, score2) > 200 else "COOKED 💀"
    }
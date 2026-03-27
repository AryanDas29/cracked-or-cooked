from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from github_fetcher import get_github_stats
from leetcode_fetcher import get_leetcode_stats
from scorer import calculate_score, get_verdict
from analyzer import analyze_github
from database import save_scan, get_leaderboard, get_user_rank

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"error": "Daily limit reached. Come back tomorrow."})

app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/compare")
@limiter.limit("10/day")
async def compare(
    request: Request,
    user1: str, user2: str,
    lc1: str = None, lc2: str = None,
    school1: str = None, school2: str = None,
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
    verdict1 = get_verdict(score1)
    verdict2 = get_verdict(score2)

    # Persist scans (save user2 only when it's a real battle, not solo self-compare)
    save_scan({**u1, "username": user1, "school": school1, "score": score1, "verdict": verdict1,
               "ai_quality_score": (ai1 or {}).get("quality_score")})
    if user1 != user2:
        save_scan({**u2, "username": user2, "school": school2, "score": score2, "verdict": verdict2,
                   "ai_quality_score": (ai2 or {}).get("quality_score")})

    return {
        "user1": {**u1, "score": score1, "verdict": verdict1, "ai_analysis": ai1},
        "user2": {**u2, "score": score2, "verdict": verdict2, "ai_analysis": ai2},
        "winner": user1 if score1 > score2 else user2,
        "winner_verdict": "CRACKED 🔥" if max(score1, score2) > 200 else "COOKED 💀"
    }


@app.get("/leaderboard")
async def leaderboard(school: str = None, limit: int = 50):
    results = get_leaderboard(school=school, limit=limit)
    return {"results": results}


@app.get("/leaderboard/search")
async def leaderboard_search(username: str):
    result = get_user_rank(username)
    return {"result": result}
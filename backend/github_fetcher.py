import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
BASE = "https://api.github.com"

async def get_github_stats(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        
        # Basic user info
        user_res = await client.get(f"{BASE}/users/{username}", headers=HEADERS)
        if user_res.status_code == 404:
            return {"error": f"GitHub user '{username}' not found"}
        user = user_res.json()

        # Repos to count stars
        repos_res = await client.get(
            f"{BASE}/users/{username}/repos?per_page=100", headers=HEADERS
        )
        repos = repos_res.json()
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)

        return {
            "username": username,
            "public_repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "total_stars": total_stars,
            "account_age_years": 2025 - int(user.get("created_at", "2020")[:4])
        }

import httpx

async def get_leetcode_stats(username: str) -> dict:
    url = "https://leetcode.com/graphql"
    query = """
    query getUserStats($username: String!) {
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
            profile {
                ranking
            }
        }
    }
    """
    async with httpx.AsyncClient() as client:
        res = await client.post(
            url,
            json={"query": query, "variables": {"username": username}},
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )

        if res.status_code != 200:
            return {"error": "LeetCode API failed"}

        data = res.json()
        user = data.get("data", {}).get("matchedUser")

        if not user:
            return {"error": f"LeetCode user '{username}' not found"}

        stats = {s["difficulty"]: s["count"] 
                 for s in user["submitStats"]["acSubmissionNum"]}

        return {
            "username": username,
            "easy_solved": stats.get("Easy", 0),
            "medium_solved": stats.get("Medium", 0),
            "hard_solved": stats.get("Hard", 0),
            "ranking": user["profile"]["ranking"]
        }

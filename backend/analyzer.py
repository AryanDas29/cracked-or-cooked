import os
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def analyze_github(username: str) -> dict:
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "type": "owner"},
            headers=headers,
        )
        repos = resp.json()

    if not isinstance(repos, list):
        return {"quality_score": 0, "analysis": "Could not fetch repos.", "verdict": "COOKED 💀"}

    top_repos = sorted(
        [r for r in repos if not r.get("fork")],
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True,
    )[:10]

    repo_lines = "\n".join(
        f"- {r['name']}: {r.get('description') or 'No description'} | "
        f"Language: {r.get('language') or 'Unknown'} | Stars: {r.get('stargazers_count', 0)}"
        for r in top_repos
    )

    prompt = f"""You are judging a developer's GitHub profile. Here are their top repos:

{repo_lines}

Respond in exactly this format with no extra text:
QUALITY_SCORE: <number 0-100>
ANALYSIS: <2 sentences about their stack and seriousness as a developer>
VERDICT: <CRACKED 🔥 or COOKED 💀>"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()

    quality_score = 0
    analysis = ""
    verdict = "COOKED 💀"

    for line in text.splitlines():
        if line.startswith("QUALITY_SCORE:"):
            try:
                quality_score = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("ANALYSIS:"):
            analysis = line.split(":", 1)[1].strip()
        elif line.startswith("VERDICT:"):
            verdict = line.split(":", 1)[1].strip()

    return {"quality_score": quality_score, "analysis": analysis, "verdict": verdict}

def calculate_score(stats: dict) -> int:
    return int(
        stats.get("hard_solved", 0) * 10 +
        stats.get("medium_solved", 0) * 4 +
        stats.get("easy_solved", 0) * 1 +
        stats.get("total_stars", 0) * 2 +
        stats.get("followers", 0) * 0.1 +
        stats.get("public_repos", 0) * 3 +
        stats.get("account_age_years", 0) * 5
    )

def get_verdict(score: int) -> str:
    if score >= 500: return "ABSOLUTELY CRACKED 🔥"
    if score >= 200: return "CRACKED 💪"
    if score >= 100: return "DECENT 📈"
    if score >= 50:  return "COOKED 😬"
    return "FULLY COOKED 💀"
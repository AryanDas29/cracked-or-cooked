import asyncio
from github_fetcher import get_github_stats
from leetcode_fetcher import get_leetcode_stats

async def main():
    github = await get_github_stats("torvalds")
    leetcode = await get_leetcode_stats("neal_wu")
    print("GitHub:", github)
    print("LeetCode:", leetcode)

asyncio.run(main())

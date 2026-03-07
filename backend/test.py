import asyncio
from github_fetcher import get_github_stats

async def main():
    result = await get_github_stats("torvalds")
    print(result)

asyncio.run(main())

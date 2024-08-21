import asyncio
import httpx
from datetime import datetime
from typing import Any, Optional


class GitHubClient:
    def __init__(self, repo_owner: str, repo_name: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        self.GITHUB_API_BASE_URL = (
            "https://api.github.com/repos/{repo_owner}/{repo_name}".format(
                repo_owner=self.repo_owner, repo_name=self.repo_name
            )
        )

    async def _get_all(self, uri: str, params=Optional[dict]) -> list[Any]:
        collected = []

        async with httpx.AsyncClient() as client:
            url = self.GITHUB_API_BASE_URL + uri

            while True:
                response = await client.get(url, params=params)
                collected += response.json()

                await asyncio.sleep(0.1)

                if response.links and "next" in response.links:
                    url = response.links["next"]["url"]
                else:
                    break

        return collected

    async def get_commits(self, since: Optional[datetime]):
        params = {
            "per_page": 100,
        }
        if since is not None:
            params["since"] = since.isoformat()

        # XXX remove, just for testing
        params["since"] = "2024-08-01T00:00:00Z"

        commits = await self._get_all("/commits", params=params)
        return commits

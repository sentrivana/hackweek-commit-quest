import asyncio
from datetime import datetime
from typing import Any, Optional

import httpx

from commitquest.consts import GITHUB_TOKEN


class GitHubClient:
    def __init__(self, repo_owner: str, repo_name: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        self.headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        self.GITHUB_API_BASE_URL = (
            "https://api.github.com/repos/{repo_owner}/{repo_name}".format(
                repo_owner=self.repo_owner, repo_name=self.repo_name
            )
        )

    async def _get_all(
        self, uri: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> list[Any]:
        params = params or {}
        headers = headers or {}

        collected = []

        async with httpx.AsyncClient() as client:
            url = self.GITHUB_API_BASE_URL + uri

            while True:
                response = await client.get(
                    url, params=params, headers=self.headers | headers
                )
                if response.status_code != 200:
                    raise RuntimeError(
                        f"Failed to fetch data from GitHub API: {response.status_code} {response.json()}"
                    )

                collected += response.json()

                if response.links and "next" in response.links:
                    url = response.links["next"]["url"]
                else:
                    break

                await asyncio.sleep(0.1)

        return collected

    async def get_commits(self, since: Optional[datetime]):
        params = {
            "per_page": 100,
        }
        if since is not None:
            params["since"] = since.isoformat() + 'Z'   # wut

        commits = await self._get_all("/commits", params=params)
        return commits

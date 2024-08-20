import asyncio
import httpx
import hashlib
import hmac
import logging
from typing import Any

from fastapi import HTTPException

from commitquest.consts import DEBUG, GITHUB_WEBHOOK_SECRET


logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, repo_owner: str, repo_name: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name

        self.GITHUB_API_BASE_URL = "https://api.github.com/repos/{repo_owner}/{repo_name}".format(repo_owner=self.repo_owner, repo_name=self.repo_name)

    async def get(self, *uris: str) -> dict[str, dict[str, Any]]:
        requests = []

        async with httpx.AsyncClient() as client:
            for uri in uris:
                requests.append(
                    client.get(
                        self.GITHUB_API_BASE_URL + uri,
                        params={
                            "per_page": 100,
                        }
                    )
                )

            responses = await asyncio.gather(*requests)

        responses = [response.json() for response in responses]

        if DEBUG:
            for response in responses:
                logger.warning(response)

        return dict(zip(uris, responses))

    @classmethod
    def verify_signature(payload_body, signature_header):
        """Verify that the payload was sent from GitHub by validating SHA256.

        Raise 403 if not authorized.

        Args:
            payload_body: original request body to verify (request.body())
            signature_header: header received from GitHub (x-hub-signature-256)
        """
        if not signature_header:
            raise HTTPException(
                status_code=403, detail="x-hub-signature-256 header is missing!"
            )

        hash_object = hmac.new(
            GITHUB_WEBHOOK_SECRET.encode("utf-8"),
            msg=payload_body,
            digestmod=hashlib.sha256,
        )
        expected_signature = "sha256=" + hash_object.hexdigest()

        if not hmac.compare_digest(expected_signature, signature_header):
            raise HTTPException(status_code=403, detail="Request signatures didn't match!")

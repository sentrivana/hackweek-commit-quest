import hashlib
import hmac
from typing import Annotated, Any

import httpx
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status

from commitquest.consts import GITHUB_WEBHOOK_SECRET

GITHUB_API_BASE_URL = "https://api.github.com/repos/{repo_owner}/{repo_name}"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="root.html", context={"id": "abc"}
    )


@app.post("/")
async def go_to_repo(
    repo_owner: Annotated[str, Form()], repo_name: Annotated[str, Form()]
):
    return RedirectResponse(
        f"/game/{repo_owner}/{repo_name}", status_code=status.HTTP_302_FOUND
    )


@app.get("/game/{repo_owner}/{repo_name}")
async def game(request: Request, repo_owner: str, repo_name: str):
    commits = await get_from_github(repo_owner, repo_name, "/commits")
    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context={"repo_owner": repo_owner, "repo_name": repo_name, "commits": commits},
    )


@app.post("/webhook")
async def webhook(request: Request):
    verify_github_signature(
        await request.body(), request.headers.get("X-Hub-Signature-256")
    )
    return await request.json()


async def get_from_github(repo_owner: str, repo_name: str, uri: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GITHUB_API_BASE_URL.format(repo_owner=repo_owner, repo_name=repo_name) + uri,
            params={
                "per_page": 100,
            }
        )

        import json

        print(json.dumps(response.json()))
        return response.json()


def verify_github_signature(payload_body, signature_header):
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

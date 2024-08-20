from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status

from commitquest.client import GitHubClient
from commitquest.consts import DEBUG


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
    github = GitHubClient(repo_owner=repo_owner, repo_name=repo_name)

    resources = await github.get("/commits")

    context = {"repo_owner": repo_owner, "repo_name": repo_name, "commits": resources["/commits"]}

    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context=context,
    )


@app.post("/webhook")
async def webhook(request: Request):
    GitHubClient.verify_signature(
        await request.body(), request.headers.get("X-Hub-Signature-256")
    )
    return await request.json()

from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from commitquest.game import Game

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="root.html", context={"id": "abc"}
    )


@router.post("/")
async def go_to_repo(
    repo_owner: Annotated[str, Form()], repo_name: Annotated[str, Form()]
):
    return RedirectResponse(
        f"/game/{repo_owner}/{repo_name}", status_code=status.HTTP_302_FOUND
    )


@router.get("/game/{repo_owner}/{repo_name}")
async def game(request: Request, repo_owner: str, repo_name: str):
    context = {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
    }

    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context=context,
    )

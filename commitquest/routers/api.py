from fastapi import APIRouter, Request

from commitquest.game import Game


router = APIRouter(prefix="/api")


@router.get("/{repo_owner}/{repo_name}/state")
async def state(request: Request, repo_owner: str, repo_name: str):
    game = Game(repo_owner=repo_owner, repo_name=repo_name)
    await game.update()

    data = game.get_state()

    return {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
    } | data

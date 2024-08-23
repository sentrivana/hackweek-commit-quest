# hackweek-commit-quest

Fight evil by pushing commits!

This is a game you actually _don't_ play.

How it works: There's a website that you can point to your repo and it will spawn a boss rush game for you. You fight the boss indirectly, by pushing commits to the repo. Everytime new commits are added, damage is dealt to the boss. All contributors of those commits show up as heroes.

That's the basic idea. The game is about 80% finished.

## How to

1. Clone the repo, `cd` into it
2. `python3 -m venv .env`
3. `source .env/bin/activate`
4. `pip install -r requirements.txt`
5. Generate a GitHub [personal access token](https://github.com/settings/apps) (no privileges necessary)
6. Open `commitquest/consts.py` and set `GITHUB_TOKEN` to your token
7. `cd` to the `commitquest` directory
8. Run `fastapi dev main.py`
9. Go to `127.0.0.1:8000`, input your repo info, and click OK

Now go make some commits and come back to `127.0.0.1:8000/game/{repo_owner}/{repo_name}` to check back your progress against the boss!

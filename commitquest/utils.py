from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from commitquest.consts import DEBUG


def calculate_author_stats(commits: list[dict[str, Any]]) -> dict[str, int]:
    authors = defaultdict(lambda: 0)

    for commit in commits:
        if not commit.get("author"):
            continue

        author = commit["author"]["login"]
        authors[author] += 1

    return authors


def debug(msg: str, repo: Optional[str] = None) -> None:
    # TODO: Make this use an actual logger I guess. Didn't feel like getting
    # into setting up logging correctly
    if DEBUG:
        if repo:
            print(f"[{repo}] {msg}")
        else:
            print(msg)

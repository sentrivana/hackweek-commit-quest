import random
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from commitquest.client import GitHubClient
from commitquest.consts import (
    BOSS_ATTRIBUTES,
    BOSS_NAMES,
    BOSS_SPRITES,
    ENVIRONMENTS,
    HERO_SPRITES,
)
from commitquest.db import engine, init_db
from commitquest.models import Boss, Hero, Level, Repo
from commitquest.utils import calculate_author_stats, debug


class Game:
    def __init__(self, repo_owner, repo_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github = GitHubClient(repo_owner=self.repo_owner, repo_name=self.repo_name)

        self.level = None
        self.boss = None
        self.heroes = []

        self.load()

    def load(self):
        debug("Loading game state from DB...", repo=self.repo_name)

        init_db()

        with Session(engine) as session:
            session.expire_on_commit = False
            repo = (
                select(Repo)
                .where(Repo.name == self.repo_name, Repo.owner == self.repo_owner)
                .options(
                    joinedload(Repo.levels).options(
                        joinedload(Level.heroes), joinedload(Level.boss)
                    )
                )
            )
            self.repo = session.exec(repo).first()

        if self.repo:
            debug("Game already exists", repo=self.repo_name)
            if self.repo.levels:
                # XXX do this like a normal person
                self.level = sorted(
                    self.repo.levels, key=lambda l: l.seq, reverse=True
                )[0]
                self.boss = self.level.boss[0]
                self.heroes = self.level.heroes

        else:
            debug("Game doesn't exist. Starting a new game", repo=self.repo_name)
            self.create_repo()

    def create_repo(self) -> None:
        self.repo = Repo(
            owner=self.repo_owner,
            name=self.repo_name,
        )

        with Session(engine) as session:
            session.expire_on_commit = False
            session.add(self.repo)
            session.commit()
            session.refresh(self.repo)

    def start_level(self):
        debug("Starting a new level", repo=self.repo_name)

        created = []

        seq = 0 if self.level is None else self.level.seq + 1

        self.level = Level(
            seq=seq,
            repo=self.repo,
            environment=random.choice(ENVIRONMENTS),
        )
        created.append(self.level)

        boss_health = max(
            self.repo.difficulty // 4 * seq
            + random.randint(0, self.repo.difficulty // 4),
            1,
        )

        self.boss = Boss(
            level=self.level,
            name=f"{random.choice(BOSS_NAMES)} {random.choice(BOSS_ATTRIBUTES)}",
            sprite=random.choice(BOSS_SPRITES),
            max_health=boss_health,
            health=boss_health,
        )
        created.append(self.boss)

        self.heroes = []

        with Session(engine) as session:
            session.expire_on_commit = False
            for instance in created:
                session.add(instance)

            session.commit()
            session.refresh(self.level)
            session.refresh(self.boss)

    def end_level(self):
        pass

    def calculate_damage(self):
        # XXX
        return 2 if len(self.commits) > 0 else 0

    async def update(self):
        debug("Fetching repo state...", repo=self.repo_name)
        now = datetime.now(timezone.utc)

        if (
            self.repo.difficulty
            is None
            # XXX fix f timezones
            # or self.repo.difficulty_updated < now - timedelta(weeks=1)
        ):
            first_time = True
            since = now - timedelta(weeks=4)
            self.commits = []
        else:
            first_time = False
            since = self.repo.updated

        commits = await self.github.get_commits(since=since)

        difficulty = None
        if first_time:
            difficulty = len(commits)
        else:
            self.commits = commits

        debug(
            f"Fetched {len(self.commits)} new commits",
            repo=self.repo_name,
        )

        if self.repo.difficulty is None:
            self.repo.difficulty = max(difficulty, 1)
            self.repo.difficulty_updated = now
            debug(
                f"Set difficulty to {self.repo.difficulty}",
                repo=self.repo_name,
            )

        if self.level is None:
            self.start_level()

        self.update_heroes()

        damage = self.calculate_damage()
        self.boss.health = max(self.boss.health - damage, 0)

        debug(
            f"{damage} damage dealt! Boss at {self.boss.health} health",
            repo=self.repo_name,
        )

        if self.boss.finished:
            self.end_level()
            self.start_level()

        with Session(engine) as session:
            session.expire_on_commit = False
            session.add(self.boss)
            session.add(self.repo)
            session.commit()

        debug(
            f"Level: {self.level} | Boss: {self.boss} | Heroes: {self.heroes}",
            repo=self.repo_name,
        )

    def update_heroes(self) -> None:
        debug("Updating heroes", repo=self.repo_name)

        hero_names = {hero.name for hero in self.heroes}

        authors = calculate_author_stats(self.commits)
        for author, contributions in authors.items():
            if author not in hero_names:
                hero = Hero(
                    name=author,
                    level=self.level,
                    power=contributions,
                    sprite=random.choice(HERO_SPRITES),
                )
                debug(f"Adding hero {hero}", repo=self.repo_name)

        with Session(engine) as session:
            session.expire_on_commit = False
            for hero in self.heroes:
                session.add(hero)
            session.commit()
            for hero in self.heroes:
                session.refresh(hero)

    def get_state(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "boss": self.boss,
            "heroes": self.heroes,
        }

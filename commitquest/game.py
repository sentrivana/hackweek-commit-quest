import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from commitquest.client import GitHubClient
from commitquest.consts import BOSS_ATTRIBUTES, BOSS_NAMES, ENVIRONMENTS, SPRITES
from commitquest.db import engine, init_db
from commitquest.models import Boss, Hero, Level, Repo
from commitquest.utils import debug


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
        """Set the game up from the DB, creating stuff if not initialized yet."""
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
                self.level = self.repo.levels[0]  # XXX ordering
                self.boss = self.level.boss[0]
                self.heroes = self.level.heroes
            else:
                self.start_level()

        else:
            debug("Game doesn't exist. Starting a new game", repo=self.repo_name)
            self.create_repo()
            self.start_level()

        debug(
            f"Level: {self.level} | Boss: {self.boss} | Heroes: {self.heroes}",
            repo=self.repo_name,
        )

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
        created = []

        seq = 0 if self.level is None else self.level.seq + 1

        self.level = Level(
            seq=seq,
            repo=self.repo,
            environment=random.choice(ENVIRONMENTS),
        )
        # XXX increase diff over time
        created.append(self.level)

        self.boss = Boss(
            level=self.level,
            name=f"{random.choice(BOSS_NAMES)} {random.choice(BOSS_ATTRIBUTES)}",
            sprite=random.choice(SPRITES),
            max_health=300,
            health=300,
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
        return 100

    async def update(self):
        debug("Fetching repo state...", repo=self.repo_name)

        if self.repo.difficulty is None:
            since = datetime.now(timezone.utc) - timedelta(weeks=4)
        else:
            since = self.repo.updated

        self.commits = await self.github.get_commits(since=since)

        debug(
            f"Fetched {len(self.commits)} new commits",
            repo=self.repo_name,
        )

        if self.repo.difficulty is None:
            self.repo.difficulty = max(len(self.commits), 1)
            debug(
                f"Set difficulty to {self.repo.difficulty}",
                repo=self.repo_name,
            )

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

    def get_state(self):
        return {
            "level": self.level,
            "boss": self.boss,
            "heroes": self.heroes,
        }

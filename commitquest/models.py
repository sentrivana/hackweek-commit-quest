from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlmodel import Field, Relationship, SQLModel


class UUIDModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TimestampModel(SQLModel):
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        }
    )


class Repo(TimestampModel, UUIDModel, table=True):
    owner: str
    name: str
    difficulty: Optional[int]

    levels: list["Level"] = Relationship(back_populates="repo")

    def __str__(self):
        return self.name


class Level(TimestampModel, UUIDModel, table=True):
    seq: int
    repo_id: UUID = Field(default=None, foreign_key="repo.id")
    environment: str

    repo: Repo = Relationship(back_populates="levels")
    heroes: list["Hero"] = Relationship(back_populates="level")
    boss: list["Boss"] = Relationship(back_populates="level")

    def __str__(self):
        return f"Level {self.seq} ({self.environment})"


class Hero(TimestampModel, UUIDModel, table=True):
    level_id: UUID = Field(default=None, foreign_key="level.id")
    name: str
    power: int
    sprite: str

    level: Level = Relationship(back_populates="heroes")

    def __str__(self):
        return f"{self.name} ({self.power})"


class Boss(TimestampModel, UUIDModel, table=True):
    level_id: UUID = Field(default=None, foreign_key="level.id")
    name: str
    sprite: str
    max_health: int
    health: int

    level: Level = Relationship(back_populates="boss")

    def __str__(self):
        return f"{self.name} ({self.max_health})"

    @property
    def finished(self):
        return self.health <= 0

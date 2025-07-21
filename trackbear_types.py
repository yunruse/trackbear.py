"""
Types returned by the Trackbear API.
"""

from dataclasses import dataclass, field
from datetime import datetime as Datetime, date as Date
from typing import Literal


def convert[T](item: T | dict, type: type[T]) -> T:
    if isinstance(item, dict):
        return type(**item)
    return item


def convertList[T](items: list[T] | list[dict], type: type[T]) -> list[T]:
    if items and isinstance(items[0], dict):
        return [type(**d) for d in items]
    return items


@dataclass
class TrackBearObject:
    id: str
    uuid: str = field(repr=False)
    createdAt: Datetime = field(repr=False)
    updatedAt: Datetime = field(repr=False)
    ownerId: str = field(repr=False)

    def __post_init__(self):
        for k in 'createdAt', 'updatedAt':
            v = getattr(self, k)
            if isinstance(v, str):
                setattr(self, k, Datetime.fromisoformat(v))


MeasureType = Literal['word', 'time', 'page', 'chapter', 'scene', 'line']


@dataclass
class Count:
    word: int = 0
    time: int = 0
    page: int = 0
    chapter: int = 0
    scene: int = 0
    line: int = 0


@dataclass
class Tag(TrackBearObject):
    name: str
    state: Literal['active', 'deleted'] | None = None
    color: str | None = None

    def __post_init__(self):
        super().__post_init__()


@dataclass
class Tally(TrackBearObject):
    state: str
    date: Date  # YYYY-MM-DD
    measure: MeasureType
    count: int
    note: str
    workId: str
    tags: list[Tag]

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.date, str):
            self.date = Date.fromisoformat(self.date)
        self.tags = convertList(self.tags, Tag)


@dataclass
class TallyWithWork(Tally):
    workId: str = field(repr=False)
    work: "Project"

    def __post_init__(self):
        super().__post_init__()
        self.work = convert(self.work, Project)


@dataclass
class Project(TrackBearObject):
    title: str

    description: str = field(repr=False)
    cover: str | None

    startingBalance: Count
    starred: bool = False
    displayOnProfile: bool = False

    state: Literal['active', 'deleted'] | None = None
    phase: Literal[
        'planning', 'outlining', 'drafting',
        'revising', 'on hold', 'finished', 'abandoned'
    ] | None = None

    def __post_init__(self):
        super().__post_init__()
        self.startingBalance = convert(self.startingBalance, Count)


@dataclass
class ProjectWithoutTallies(Project):
    lastUpdated: str | None = field(default=None, repr=False)
    totals: Count = field(default_factory=Count)

    def __post_init__(self):
        super().__post_init__()
        self.totals = convert(self.totals, Count)


@dataclass
class ProjectWithTallies(Project):
    tallies: list[Tally] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.tallies = convertList(self.tallies, Tally)

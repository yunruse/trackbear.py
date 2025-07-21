"""
Types returned by the Trackbear API.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime as Datetime, date as Date
from types import NotImplementedType
from typing import TYPE_CHECKING, ClassVar, Literal


if TYPE_CHECKING:
    from .trackbear import TrackBearAPI


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
    id: str = field(repr=False)
    uuid: str = field(repr=False)
    createdAt: Datetime = field(repr=False)
    updatedAt: Datetime = field(repr=False)
    ownerId: str = field(repr=False)

    def __post_init__(self):
        for k in 'createdAt', 'updatedAt':
            v = getattr(self, k)
            if isinstance(v, str):
                setattr(self, k, Datetime.fromisoformat(v))

    __tb: "TrackBearAPI" = field(init=False, repr=False, default=None)

    def _tb(self, tb: "TrackBearAPI"):
        self.__tb = tb
        return self

    @property
    def _trackbear(self):
        if self.__tb is None:
            raise ValueError(
                f"Somehow this {type(self).__name__}"
                " was not instantiated from a TrackBearAPI,"
                " so cannot use this method."
            )
        return self.__tb


MeasureType = Literal['word', 'time', 'page', 'chapter', 'scene', 'line']
State = Literal['active', 'deleted']


@dataclass
class Count:
    word: int = 0
    time: int = 0
    page: int = 0
    chapter: int = 0
    scene: int = 0
    line: int = 0

    def __add__(self, other: "Count | Tally"):
        total = asdict(self)
        if isinstance(other, Tally):
            total[other.measure] += other.count
        else:
            for k, v in asdict(other).items():
                total[k] += v
        return Count(**total)


Color = Literal[
    "default", "red", "orange", "yellow", "green",
    "blue", "purple", "brown", "white", "black", "gray"]


@dataclass
class Tag(TrackBearObject):
    name: str
    state: State | None = field(repr=False, default=None)
    color: Color | None = None

    def delete(self):
        self._trackbear.delete_tag(self.id)


@dataclass
class Tally(TrackBearObject):
    state: str
    date: Date  # YYYY-MM-DD
    measure: MeasureType
    count: int
    note: str
    workId: int
    tags: list[Tag]

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.date, str):
            self.date = Date.fromisoformat(self.date)
        self.tags = convertList(self.tags, Tag)

    def _tb(self, tb):
        for t in self.tags:
            t._tb(tb)
        return super()._tb(tb)

    def delete(self):
        self._trackbear.delete_tally(self.id)


@dataclass
class TallyWithoutWork(Tally):
    __qualname__ = 'Tally'

    @property
    def work(self):
        return self._trackbear.tally(self.workId)


@dataclass
class TallyWithWork(Tally):
    __qualname__ = 'Tally'

    work: "Project" = field()

    def __post_init__(self):
        super().__post_init__()
        self.work = convert(self.work, Project)

    def _tb(self, tb):
        self.work._tb(tb)
        return super()._tb(tb)


@dataclass
class Project(TrackBearObject):
    title: str

    description: str = field(repr=False)
    cover: str | None

    startingBalance: Count
    starred: bool = False
    displayOnProfile: bool = False

    state: State | None = field(repr=False, default=None)
    phase: Literal[
        'planning', 'outlining', 'drafting',
        'revising', 'on hold', 'finished', 'abandoned'
    ] | None = None

    def __post_init__(self):
        super().__post_init__()
        self.startingBalance = convert(self.startingBalance, Count)

    totals: ClassVar[Count]
    tallies: ClassVar[list[Tally]]
    lastUpdated: ClassVar[NotImplementedType] = field(init=False, repr=False)

    def delete(self):
        self._trackbear.delete_project(self.id)


@dataclass
class ProjectWithoutTallies(Project):
    __qualname__ = 'Project'

    lastUpdated: str | None = field(default=None, repr=False)
    totals: Count = field(default_factory=Count)

    def __post_init__(self):
        super().__post_init__()
        self.totals = convert(self.totals, Count)

    @property
    def tallies(self):
        return self._trackbear.project(self.id).tallies


@dataclass
class ProjectWithTallies(Project):
    __qualname__ = 'Project'

    tallies: list[Tally] = field(default_factory=list)

    @property
    def totals(self):
        return sum(self.tallies, start=self.startingBalance)

    def __post_init__(self):
        super().__post_init__()
        self.tallies = convertList(self.tallies, Tally)

    def _tb(self, tb):
        for t in self.tallies:
            t._tb(tb)
        return super()._tb(tb)

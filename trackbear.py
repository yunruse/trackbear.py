from dataclasses import dataclass, field
from typing import Literal

from datetime import date as Date

import requests

from trackbear_types import MeasureType, Project, ProjectWithTallies, ProjectWithoutTallies, Tag, Tally, TallyWithWork

Method = Literal['GET', 'POST']


class InvalidToken(Exception):
    pass


class APIError(Exception):
    pass


@dataclass
class TrackBearAPI:
    """
    The TrackBear API.

    Some methods may raise a HTTPError 404 if a specific element doesn't exist.
    """

    api_key: str = field(repr=False)
    api_url: str = "https://trackbear.app/api/v1"

    def __post_init__(self):
        self._request('GET', '/ping/api-token')

    def _request(
        self,
        method: Method,
        url: str,
        json: dict = None,
    ) -> dict:
        response = requests.request(
            method=method,
            url=self.api_url + url,
            headers={
                'User-Agent': 'github.com/yunruse/trackbear.py by mia@yunru.se',
                'Authorization': f'Bearer {self.api_key}',
            },
            json=json,
        )
        if response.status_code == 401:
            raise InvalidToken(response.json()['error']['message'])
        if response.status_code == 400:
            raise APIError(response.json()['error']['message'])
        response.raise_for_status()

        json = response.json()
        assert json['success']
        return json['data']

    def projects(self) -> list[Project]:
        "Get all of the user's projects."
        return [ProjectWithoutTallies(**p)._tb(self) for p in self._request('GET', '/project')]

    def project(self, id: int) -> Project:
        "Get a specific project."
        return ProjectWithTallies(**self._request('GET', f'/project/{id}'))._tb(self)

    def tallies(self) -> list[Tally]:
        "Get all of the user's tallies."
        return [TallyWithWork(**t)._tb(self) for t in self._request('GET', f'/tally')]

    def tally(self, id: int) -> Tally:
        "Get a specific tally."
        return TallyWithWork(**self._request('GET', f'/tally/{id}'))._tb(self)

    def add_tally(
        self,
        project: Project | str | int,
        count: int,
        measure: MeasureType = 'word',
        date: Date = None,
        set_total: bool = False,
        note: str = "",

        tags: list[str] = None
    ) -> Tally:
        if isinstance(project, Project):
            project = project.id

        date = date or Date.today()
        if isinstance(date, Date):
            date = date.isoformat()

        result = self._request('POST', '/tally', {
            'date': date,
            'measure': measure,
            'count': count,
            'note': note,
            'workId': int(project),
            'setTotal': set_total,
            'tags': tags or [],
        })
        return TallyWithWork(**result)._tb(self)

    def tags(self):
        "Get all of the user's tags."
        return [Tag(**t)._tb(self) for t in self._request('GET', f'/tag')]

    def tag(self, id: int):
        "Get a specific tag."
        return Tag(**self._request('GET', f'/tag/{id}'))._tb(self)

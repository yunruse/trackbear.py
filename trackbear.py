from dataclasses import asdict, dataclass, field
from typing import Literal

from datetime import date as Date

import requests

from trackbear_types import Color, Count, MeasureType, Project, ProjectWithTallies, ProjectWithoutTallies, Tag, Tally, TallyWithWork

Method = Literal['GET', 'POST', 'DELETE']


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

    # 88888888ba                            88
    # 88      "8b                           ""                            ,d
    # 88      ,8P                                                         88
    # 88aaaaaa8P'  8b,dPPYba,   ,adPPYba,   88   ,adPPYba,   ,adPPYba,  MM88MMM  ,adPPYba,
    # 88""""""'    88P'   "Y8  a8"     "8a  88  a8P_____88  a8"     ""    88     I8[    ""
    # 88           88          8b       d8  88  8PP"""""""  8b            88      `"Y8ba,
    # 88           88          "8a,   ,a8"  88  "8b,   ,aa  "8a,   ,aa    88,    aa    ]8I
    # 88           88           `"YbbdP"'   88   `"Ybbd8"'   `"Ybbd8"'    "Y888  `"YbbdP"'
    #                                      ,88
    #                                    888P"

    def projects(self) -> list[Project]:
        "Get all of the user's projects."
        return [ProjectWithoutTallies(**p)._tb(self) for p in self._request('GET', '/project')]

    def project(self, id: int) -> Project:
        "Get a specific project."
        return ProjectWithTallies(**self._request('GET', f'/project/{id}'))._tb(self)

    def create_project(
        self,
        title: str,
        description: str = "",
        phase: str = "planning",
        starred: bool = False,
        display_on_profile: bool = False,
        starting_balance: Count = None
    ):

        result = self._request('POST', '/project', {
            "title": title,
            "description": description,
            "phase": phase,
            "starred": starred,
            "displayOnProfile": display_on_profile,
            "startingBalance": asdict(starting_balance or Count())
        })
        return ProjectWithTallies(**result)._tb(self)

    def delete_project(self, id: int):
        "Delete a tally."
        self._request('DELETE', f'/project/{id}')

    # 888888888888         88  88  88
    #      88              88  88  ""
    #      88              88  88
    #      88  ,adPPYYba,  88  88  88   ,adPPYba,  ,adPPYba,
    #      88  ""     `Y8  88  88  88  a8P_____88  I8[    ""
    #      88  ,adPPPPP88  88  88  88  8PP"""""""   `"Y8ba,
    #      88  88,    ,88  88  88  88  "8b,   ,aa  aa    ]8I
    #      88  `"8bbdP"Y8  88  88  88   `"Ybbd8"'  `"YbbdP"'

    def tallies(self) -> list[Tally]:
        "Get all of the user's tallies."
        return [TallyWithWork(**t)._tb(self) for t in self._request('GET', f'/tally')]

    def tally(self, id: int) -> Tally:
        "Get a specific tally."
        return TallyWithWork(**self._request('GET', f'/tally/{id}'))._tb(self)

    def create_tally(
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

    def delete_tally(self, id: int):
        "Delete a tally."
        self._request('DELETE', f'/tally/{id}')

    # 888888888888
    #      88
    #      88
    #      88  ,adPPYYba,   ,adPPYb,d8  ,adPPYba,
    #      88  ""     `Y8  a8"    `Y88  I8[    ""
    #      88  ,adPPPPP88  8b       88   `"Y8ba,
    #      88  88,    ,88  "8a,   ,d88  aa    ]8I
    #      88  `"8bbdP"Y8   `"YbbdP"Y8  `"YbbdP"'
    #                       aa,    ,88
    #                        "Y8bbdP"

    def tags(self):
        "Get all of the user's tags."
        return [Tag(**t)._tb(self) for t in self._request('GET', f'/tag')]

    def tag(self, id: int):
        "Get a specific tag."
        return Tag(**self._request('GET', f'/tag/{id}'))._tb(self)

    def create_tag(
        self,
        name: str,
        color: Color = 'default',
    ):
        result = self._request('POST', '/tag', {
            'name': name,
            'color': color,
        })
        return Tag(**result)._tb(self)

    def delete_tag(self, id: int):
        "Delete a tag."
        self._request('DELETE', f'/tag/{id}')

from dataclasses import dataclass, field
from typing import Literal

import requests

from trackbear_types import ProjectWithTallies, ProjectWithoutTallies, Tag, Tally, TallyWithWork

Method = Literal['GET', 'POST']


class InvalidToken(Exception):
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
    ) -> dict:
        response = requests.request(
            method=method,
            url=self.api_url + url,
            headers={
                'User-Agent': 'github.com/yunruse/trackbear.py by mia@yunru.se',
                'Authorization': f'Bearer {self.api_key}',
            }
        )
        if response.status_code == 401:
            raise InvalidToken(response.json()['error']['message'])
        response.raise_for_status()

        json = response.json()
        assert json['success']
        return json['data']

    def projects(self):
        "Get all of the user's projects."
        return [ProjectWithoutTallies(**p) for p in self._request('GET', '/project')]

    def project(self, id: int):
        "Get a specific project."
        return ProjectWithTallies(**self._request('GET', f'/project/{id}'))

    def tallies(self):
        "Get all of the user's tallies."
        return [TallyWithWork(**t) for t in self._request('GET', f'/tally')]

    def tally(self, id: int):
        "Get a specific tally."
        return TallyWithWork(**self._request('GET', f'/tally/{id}'))

    def tags(self):
        "Get all of the user's tags."
        return [Tag(**t) for t in self._request('GET', f'/tag')]

    def tag(self, id: int):
        "Get a specific tag."
        return Tag(**self._request('GET', f'/tag/{id}'))

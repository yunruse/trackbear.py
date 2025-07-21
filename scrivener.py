from dataclasses import dataclass
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup


DAY_PARAMS = {
    'owc': {'name': 'other_words', 'func': int},
    'occ': {'name': 'other_chars', 'func': int},
    'dwc': {'name': 'draft_words', 'func': int},
    'dcc': {'name': 'draft_chars', 'func': int},
    'dtwc': {'name': 'draft_words_total', 'func': int},
    'dtcc': {'name': 'draft_chars_total', 'func': int},
    's': {'name': 'session_target', 'func': int},
    'st': {'name': 'session_type', 'func': str},
}


@dataclass
class Day:
    other_words: int
    other_chars: int
    draft_words: int
    draft_chars: int
    draft_words_total: int | None = None
    draft_chars_total: int | None = None
    session_target: int | None = None
    session_type: str | None = None


class WritingHistory(dict[date, Day]):
    @classmethod
    def from_scriv(cls, fp: str):
        with open(Path(fp) / 'Files' / 'writing.history') as f:
            soup = BeautifulSoup(f, features='xml')

        return cls({
            date.fromisoformat(day.text): Day(**{
                DAY_PARAMS[k]['name']: DAY_PARAMS[k]['func'](v)
                for k, v in day.attrs.items()
            })
            for day in soup.find_all('Day')
        })

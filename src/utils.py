from dataclasses import dataclass, is_dataclass, field
from typing import Literal
import math
import json

from github import LANGUAGE_ALIASES

DEFAULT_PARAMS = {
    "affiliation": "owner",
    "include_forks": True,
    "stop_below": 1  # Don't show less than a certain percentage
}


@dataclass
class Lang:
    name: str
    bbytes: int


@dataclass
class Repo:
    name: str
    fork: bool
    languages: dict[str, Lang]


@dataclass
class Place:
    anchor: int
    image_begin: int
    image_end: int
    hide: set[str] = field(default_factory=set)
    replace: dict[str, str] = field(default_factory=dict)
    affiliation: Literal["all", "owner"] = DEFAULT_PARAMS["affiliation"]
    include_forks: bool = DEFAULT_PARAMS["include_forks"]


@dataclass
class SvgPos:
    x: int
    y: int
    width: int
    height: int


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return str(o)
        return super().default(o)


def check_lang_exists(lang: str) -> None:
    assert lang in LANGUAGE_ALIASES, (
        f'Language "{lang}" not found in linguist library ('
        "https://github.com/github/linguist/blob/master/lib/linguist/languages.yml"
        ")"
    )
    return lang


# Pretty-pring amount of bytes
SIZE_NAME = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def print_bytes(size_bytes: int) -> str:
    if not size_bytes:
        return "0B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    return f"{s}{SIZE_NAME[i]}"

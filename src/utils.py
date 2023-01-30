from dataclasses import dataclass, is_dataclass, field
import math
import json

from github import LANGUAGE_ALIASES

DEFAULT_PARAMS = {
    "include_forks": False,
    "include_collaborative": False,
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
    collaborative: bool
    languages: dict[str, Lang]


@dataclass
class Place:
    anchor: int
    image_begin: int
    image_end: int
    hide: set[str] = field(default_factory=set)
    replace: dict[str, str] = field(default_factory=dict)
    include_forks: bool = DEFAULT_PARAMS["include_forks"]
    include_collaborative: bool = DEFAULT_PARAMS["include_collaborative"]


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


def check_lang_exists(lang: str) -> str:
    assert lang in LANGUAGE_ALIASES, (
        f'Language "{lang}" not found in linguist library ('
        "https://github.com/github/linguist/blob/master/lib/linguist/languages.yml"
        ")"
    )
    return lang


def check_repo_format(repo: str) -> str:
    assert 0 < repo.find('/') < len(repo) - 1 and repo.count('/') == 1, (
        r'Repo name should be in format {repo_owner}/{repo_name}, for example: "octocat/hello-worId"'
    )
    return repo


# Pretty-pring amount of bytes
SIZE_NAME = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def print_bytes(size_bytes: int) -> str:
    if not size_bytes:
        return "0B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 1)
    return f"{s}{SIZE_NAME[i]}"

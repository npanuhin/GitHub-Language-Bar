from dataclasses import dataclass, is_dataclass
import json


@dataclass
class Lang:
    tag: str
    name: str
    bbytes: int


@dataclass
class Place:
    image_begin: int
    image_end: int
    anchor_begin: int
    exclude: set[str]
    replace: dict[str, str]


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

# from collections import defaultdict
from urllib.parse import parse_qsl
from itertools import chain
from typing import Optional
from copy import deepcopy
import sys
import os
import re

sys.path.append("src")
from src.utils import Lang, Place            # noqa
from src.github import GitHub                # noqa
from src.svg import generate_bar, beautify   # noqa


GH_TOKEN = os.environ.get("GH_TOKEN")
if GH_TOKEN is None:
    with open(".gh_token", encoding="utf-8") as file:
        GH_TOKEN = file.read().strip()

GITHUB = GitHub(GH_TOKEN)


ANCHOR_REGEX = re.compile(r"^(.+?)? ?(<!--\s+Langbar(\?.*)?\s+-->)$", re.MULTILINE | re.IGNORECASE)
ANCHOR_REPLACEMENT = "<!-- Langbar{query} -->{langbar}"

DEFAULT_PARAMS = {
    "stop_below": 1  # Don't show less than a certain percentage
}


def tagify(string: str) -> str:
    return string.strip().lower().replace(' ', '_')


def get_my_languages(exclude: Optional[set] = None) -> dict[str, Lang]:
    languages = {}

    print("Fetching repositories...")
    repositories = list(GITHUB.get_my_repos())
    # with open("data.json", 'w', encoding="utf-8") as file:
    #     json.dump(repositories, file, ensure_ascii=False, indent=4)

    print("Fetching languages...")
    for i, repository in enumerate(repositories):  # TODO DEBUG
        for lang_name, bbytes in GITHUB.get_repo_languages(repository["full_name"]).items():
            if not exclude or tagify(lang_name) not in exclude:
                lang_obj = languages.get(tagify(lang_name), Lang(tagify(lang_name), lang_name, bbytes))
                lang_obj.bbytes += bbytes
                languages[lang_obj.tag] = lang_obj
        if i % 10 == 9:
            print(f"{i + 1}/{len(repositories)}")
    print(f"{len(repositories)}/{len(repositories)}")

    # with open("lang_dump.json", 'w', encoding="utf-8") as file:
    #     json.dump(languages, file, ensure_ascii=False, indent=4, cls=DataclassJSONEncoder)

    return languages


def process_readme(readme_path: str = "README.md") -> None:
    if not os.path.isfile(readme_path):
        exit(f"{readme_path}: file not found")

    with open(readme_path, encoding="utf-8") as file:
        readme_data = file.read()

    places = []
    for match in re.finditer(ANCHOR_REGEX, readme_data):
        query = parse_qsl((match.group(3) or '').lstrip('?'))

        exclude_langs = set()
        replace_langs = {}

        for key, value in query:
            key = tagify(key)
            if key == "exclude":
                exclude_langs.update(map(tagify, value.split(',')))
            elif key == "replace":
                replace_langs.update([map(tagify, value.split(',')[:2])])

        places.append(Place(match.start(), match.span(1)[1], match.span(2)[1], exclude_langs, replace_langs))

    all_languages = get_my_languages(exclude=set(chain.from_iterable(place.exclude for place in places)))

    print()
    for place in places:
        print(f"Handling anchor in {place.anchor_begin}:")
        languages = deepcopy(all_languages)
        # print(languages)
        for replace_from, replace_to in place.replace.items():
            if replace_from in languages and replace_to in languages:
                languages[replace_to].bbytes += languages.pop(replace_from).bbytes

        languages = list(languages.values())

        total_bytes = sum(lang.bbytes for lang in languages)
        for lang in sorted(languages, key=lambda item: -item.bbytes):
            print(f"{lang.name}: {lang.bbytes}/{total_bytes} = {round(lang.bbytes * 100 / total_bytes, 2)}%")

        print(languages, total_bytes)

        # Generate SVG
        svg_bar = generate_bar(languages, total_bytes)
        with open("output/bar.svg", 'w', encoding="utf-8") as file:
            file.write(svg_bar)
        with open("output/bar.readable.svg", 'w', encoding="utf-8") as file:
            file.write(beautify(svg_bar))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for readme_path in sys.argv[1:]:
            process_readme(readme_path)
    else:
        process_readme()

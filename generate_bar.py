from urllib.parse import parse_qsl
from copy import deepcopy
# import json
import sys
import os
import re

sys.path.append("src")
from src.utils import Lang, Place                           # noqa
from src.github import GitHub                               # noqa
from src.svg import generate_bar, beautify as svg_beautify  # noqa


GH_TOKEN = os.environ.get("GH_TOKEN")
if GH_TOKEN is None:
    with open(".gh_token", encoding="utf-8") as file:
        GH_TOKEN = file.read().strip()

GITHUB = GitHub(GH_TOKEN)

PUBLISH_BRANCH = "language-bar"
PROMOTION_URL = "https://github.com/npanuhin/GitHub-Language-Bar"


ANCHOR_REGEX = re.compile(r"^(.+?)? ?(<!--\s+Langbar(\?.*)?\s+-->)$", re.MULTILINE | re.IGNORECASE)
ANCHOR_REPLACEMENT = "<!-- Langbar{query} -->{langbar}"

DEFAULT_PARAMS = {
    "stop_below": 1  # Don't show less than a certain percentage
}


def tagify(string: str) -> str:
    return string.strip().lower().replace(' ', '_')


def get_my_languages() -> dict[str, Lang]:
    languages = {}

    print("Fetching repositories...")
    repositories = list(GITHUB.get_my_repos())
    print(f"Found {len(repositories)} repositories")
    # with open("output/repos.json", 'w', encoding="utf-8") as file:
    #     json.dump(repositories, file, ensure_ascii=False, indent=4)

    print("Fetching languages...")
    for i, repository in enumerate(repositories):
        for lang_name, bbytes in GITHUB.get_repo_languages(repository["full_name"]).items():
            lang_obj = languages.get(tagify(lang_name), Lang(tagify(lang_name), lang_name, bbytes))
            lang_obj.bbytes += bbytes
            languages[lang_obj.tag] = lang_obj
        if i % 10 == 9:
            print(f"{i + 1}/{len(repositories)}")
    print(f"{len(repositories)}/{len(repositories)}")

    # with open("lang_dump.json", 'w', encoding="utf-8") as file:
    #     json.dump(languages, file, ensure_ascii=False, indent=4, cls=DataclassJSONEncoder)

    return languages


def process_readme(readme_path: str = "README.md", repo_name: str = "example/example") -> None:
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
                replace_from, replace_to = map(tagify, value.split(',')[:2])
                replace_langs[replace_from] = replace_to

        places.append(Place(
            anchor=match.span(2)[0],
            image_begin=match.start() if match.span(1)[0] == -1 else match.span(1)[0],
            image_end=match.start() if match.span(1)[1] == -1 else match.span(1)[1],
            exclude=exclude_langs,
            replace=replace_langs
        ))

    all_languages = get_my_languages()

    print()
    for place in places:
        print(f"Handling anchor in {place.anchor}:")
        print(place)
        languages = deepcopy(all_languages)
        # print(languages)

        for replace_from, replace_to in place.replace.items():
            if replace_from in languages and replace_to in languages:
                languages[replace_to].bbytes += languages.pop(replace_from).bbytes

        for exclude_lang in place.exclude:
            del languages[exclude_lang]

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
            file.write(svg_beautify(svg_bar))

        result_url = f"https://raw.githubusercontent.com/{repo_name}/language-bar/bar.svg"

        print(f"Result image: {result_url}")

        md_image = f'[<img src="{result_url}" width="100%">]({PROMOTION_URL})'
        readme_data = readme_data[:place.image_begin] + md_image + readme_data[place.image_end:]

    with open(readme_path, 'w', encoding="utf-8") as file:
        file.write(readme_data)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_readme(*sys.argv[1:3])
    else:
        print("--- Not enough arguments passed, running debug/dev mode ---\n")
        process_readme("../npanuhin/README.md", "npanuhin/npanuhin")

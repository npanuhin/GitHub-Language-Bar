from collections import defaultdict
from urllib.parse import parse_qsl
from copy import deepcopy
# import json
import sys
import os
import re

sys.path.append("src")
from src.utils import Lang, Place, DataclassJSONEncoder, check_lang_exists, print_bytes  # noqa
from src.github import GitHub, LANGUAGE_ALIASES                                          # noqa
from src.svg import generate_bar, beautify as svg_beautify                               # noqa


ONLY_PUBLIC = False
GH_TOKEN = os.environ.get("GH_TOKEN")
if GH_TOKEN is None:
    if os.path.isfile(".gh_token"):
        with open(".gh_token", encoding="utf-8") as file:
            GH_TOKEN = file.read().strip()
    else:
        ONLY_PUBLIC = True
        print("GitHub API token not specified, running in ONLY_PUBLIC mode")

GITHUB = GitHub(GH_TOKEN, only_public=ONLY_PUBLIC)

PUBLISH_BRANCH = "language-bar"
PROMOTION_URL = "https://github.com/npanuhin/GitHub-Language-Bar"


ANCHOR_REGEX = re.compile(r"^(.+?)? ?(<!--\s+Langbar(\?.*)?\s+-->)$", re.MULTILINE | re.IGNORECASE)
ANCHOR_REPLACEMENT = "<!-- Langbar{query} -->{langbar}"


def get_my_languages() -> dict[str, dict[str, Lang]]:
    full_data = defaultdict(dict)

    print("Fetching repositories...")
    repositories = list(GITHUB.get_my_repos())
    print(f"Found {len(repositories)} repositories")
    # with open("output/repos.json", 'w', encoding="utf-8") as file:
    #     json.dump(repositories, file, ensure_ascii=False, indent=4)

    print("Fetching languages...")
    for i, repository in enumerate(repositories):
        repo_name = repository["full_name"]
        repo_data = full_data[repo_name]
        for lang_name, bbytes in GITHUB.get_repo_languages(repo_name).items():
            lang_name = LANGUAGE_ALIASES[lang_name]
            if lang_name not in repo_data:
                repo_data[lang_name] = Lang(lang_name, 0)
            repo_data[lang_name].bbytes += bbytes
        if i % 10 == 9:
            print(f"{i + 1}/{len(repositories)}")
    print(f"{len(repositories)}/{len(repositories)}")

    # with open("output/repo_data.dump.json", 'w', encoding="utf-8") as file:
    #     json.dump(full_data, file, ensure_ascii=False, indent=4, cls=DataclassJSONEncoder)

    return full_data


def process_readme(readme_path: str = "README.md", readme_repo_name: str = "example/example") -> None:
    GITHUB.username = readme_repo_name.split("/")[0]
    if not os.path.isfile(readme_path):
        exit(f"{readme_path}: file not found")

    with open(readme_path, encoding="utf-8") as file:
        readme_data = file.read()

    places = []
    for match in re.finditer(ANCHOR_REGEX, readme_data):
        query = parse_qsl((match.group(3) or '').lstrip('?'))

        places.append(place := Place(
            anchor=match.span(2)[0],
            image_begin=match.start() if match.span(1)[0] == -1 else match.span(1)[0],
            image_end=match.start() if match.span(1)[1] == -1 else match.span(1)[1]
        ))

        for key, value in query:
            key = key.strip().lower()
            if key == "hide":
                for item in value.split(','):
                    if ':' in item:
                        repo, lang = map(str.strip, item.split(':'))
                        place.hide.add((repo, check_lang_exists(lang)))
                    else:
                        place.hide.add(item.strip())
            elif key == "replace":
                replace_from, replace_to = map(check_lang_exists, map(str.strip, value.split(',')[:2]))
                place.replace[replace_from] = replace_to
            elif key == "include_forks":
                place.include_forks = (value.strip().lower() in ("yes", "true", "1"))
            elif key == "affiliation":
                value = value.strip().lower()
                assert value in ("all", "owner"), "`affiliation` key only allows these values: `all`/`owner`"
                place.affiliation = value
            else:
                print(f"Undefined key: {key}")

    full_data = get_my_languages()

    if ONLY_PUBLIC:
        print("\nLanguage info:")
        for repo_name, repo_data in full_data.items():
            print(f"Languages for {repo_name}")
            for lang_name, lang in repo_data.items():
                border_symbol = '└' if lang_name == next(reversed(repo_data)) else '├'
                print(f"  {border_symbol} {lang_name}: {lang.bbytes}")

    for place in places:
        print(f"\nHandling {place}:")
        data = deepcopy(full_data)

        # Replace
        for repo_data in data.values():
            for replace_from, replace_to in place.replace.items():
                if replace_from in repo_data:
                    if replace_to not in repo_data:
                        repo_data[replace_to] = Lang(replace_to, 0)
                    repo_data[replace_to].bbytes += repo_data.pop(replace_from).bbytes

        # Hide/exclude
        for repo_name, repo_data in data.items():
            for lang_name in list(repo_data.keys()):
                if (repo_name, lang_name) in place.hide or lang_name in place.hide:
                    del repo_data[lang_name]

        languages = {}
        for repo_data in data.values():
            for lang_name, lang in repo_data.items():
                if lang_name not in languages:
                    languages[lang_name] = Lang(lang_name, 0)
                languages[lang_name].bbytes += lang.bbytes
        languages = list(languages.values())

        total_bytes = sum(lang.bbytes for lang in languages)
        print(f"──┤ Total bytes of code: {print_bytes(total_bytes)} ├──")

        for lang in sorted(languages, key=lambda item: -item.bbytes):
            hidden = " [HIDDEN]" if lang.name in place.hide else ""
            print(f"{lang.name}: {print_bytes(lang.bbytes)} = {round(lang.bbytes * 100 / total_bytes, 2)}%{hidden}")

        # Generate SVG
        svg_bar = generate_bar(languages, total_bytes)
        with open("output/bar.svg", 'w', encoding="utf-8") as file:
            file.write(svg_bar)
        with open("output/bar.readable.svg", 'w', encoding="utf-8") as file:
            file.write(svg_beautify(svg_bar))

        result_url = f"https://raw.githubusercontent.com/{readme_repo_name}/language-bar/bar.svg"

        print(f"Result image: {result_url}")
        # md_image = f'''
        # <picture>
        #     <source media="(prefers-color-scheme: dark)" srcset="{result_url}">
        #     <source media="(prefers-color-scheme: light)" srcset="{result_url}">
        #     <img src="{result_url}" width="100%">
        # </picture>
        # '''
        # md_image = re.sub(r"^ *|\n *| *$", "", md_image)
        # md_image = f'<a href="{PROMOTION_URL}">{md_image}</a>'

        md_image = f'[<img src="{result_url}" width="100%">]({PROMOTION_URL})'
        readme_data = readme_data[:place.image_begin] + md_image + readme_data[place.image_end:]

    with open(readme_path, 'w', encoding="utf-8") as file:
        file.write(readme_data)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        process_readme(*sys.argv[1:3])
    else:
        print("─── Not enough arguments passed, running debug/dev mode ───\n")
        process_readme("../npanuhin/README.md", "npanuhin/npanuhin")

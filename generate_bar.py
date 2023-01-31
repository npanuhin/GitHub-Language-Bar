from urllib.parse import parse_qsl
from copy import deepcopy
# import json
import sys
import os
import re

sys.path.append("src")
from src.utils import Lang, Repo, Place, DataclassJSONEncoder, check_lang_exists, check_repo_format, print_bytes  # noqa
from src.github import GitHub, LANGUAGE_ALIASES                                                                   # noqa
from src.svg import generate_bar, beautify as svg_beautify                                                        # noqa


ONLY_PUBLIC = False
GH_TOKEN = os.environ.get("GH_TOKEN")
if not GH_TOKEN:
    if os.path.isfile(".gh_token"):
        print("Found GitHub API token in `.gh_token` file")
        with open(".gh_token", encoding="utf-8") as file:
            GH_TOKEN = file.read().strip()
    else:
        ONLY_PUBLIC = True
        print("GitHub API token not specified, running in ONLY_PUBLIC mode")
else:
    print("Found GitHub API token in $GH_TOKEN environmental variable")

GITHUB = GitHub(GH_TOKEN, only_public=ONLY_PUBLIC)

PUBLISH_BRANCH = "language-bar"
PROMOTION_URL = "https://github.com/npanuhin/GitHub-Language-Bar"

LOG = ONLY_PUBLIC


ANCHOR_REGEX = re.compile(r"^(.+?)? ?(<!--\s+Langbar(\?.*)?\s+-->)$", re.MULTILINE | re.IGNORECASE)
ANCHOR_REPLACEMENT = "<!-- Langbar{query} -->{langbar}"


def get_my_languages() -> list[Repo]:
    repos = []

    print("Fetching repositories...")
    repositories = list(GITHUB.get_my_repos())
    if LOG:
        print(f"Found {len(repositories)} repositories")
    # with open("output/repos.json", 'w', encoding="utf-8") as file:
    #     json.dump(repositories, file, ensure_ascii=False, indent=4)

    print("Fetching languages...")
    for i, repository in enumerate(repositories):
        repo_name = repository["full_name"]
        languages = {}
        for lang_name, bbytes in GITHUB.get_repo_languages(repo_name).items():
            lang_name = LANGUAGE_ALIASES[lang_name]
            if lang_name not in languages:
                languages[lang_name] = Lang(lang_name, 0)
            languages[lang_name].bbytes += bbytes
        repos.append(Repo(
            name=repo_name,
            fork=repository["fork"],
            collaborative=(repository["owner"]["login"] != GITHUB.username),
            languages=languages
        ))
        if LOG and i % 10 == 9:
            print(f"{i + 1}/{len(repositories)}")
    if LOG:
        print(f"{len(repositories)}/{len(repositories)}")

    # with open("output/repos_data.dump.json", 'w', encoding="utf-8") as file:
    #     json.dump(repos, file, ensure_ascii=False, indent=4, cls=DataclassJSONEncoder)
    return repos


def process_readme(
    readme_path: str = "README.md", readme_repo_name: str = "example/example", enable_log: str | bool = False
) -> None:
    global LOG
    if isinstance(enable_log, str):
        enable_log = (enable_log != "false")
    LOG = enable_log or ONLY_PUBLIC
    print("Log enabled" if LOG else "Log disabled")

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
                        place.hide.add((check_repo_format(repo), check_lang_exists(lang)))
                    else:
                        place.hide.add(item.strip())

            elif key == "replace":
                for item in value.split(','):
                    assert '->' in item, '"->" not found in replace setting'
                    replace_from, replace_to = item.split('->')
                    assert ':' not in replace_to, \
                        'You cannot replace "repo1:language1" with "repo2:language2", only with "language2"'
                    if ':' in replace_from:
                        repo, lang = map(str.strip, replace_from.split(':'))
                        replace_from = check_repo_format(repo) + ':' + check_lang_exists(lang)
                    replace_to = check_lang_exists(replace_to.strip())
                    place.replace[replace_from] = replace_to

            elif key == "include_forks":
                place.include_forks = (value.strip().lower() in ("yes", "true", "1"))
            elif key == "include_collaborative":
                place.include_collaborative = (value.strip().lower() in ("yes", "true", "1"))
            else:
                print(f"Undefined key: {key}")

    default_repos = get_my_languages()

    if LOG:
        print("\n─── Language info (size in bytes) ───")
        for repo in default_repos:
            print(f"Languages for {repo.name}")
            for lang_name, lang in repo.languages.items():
                border_symbol = '└' if lang_name == next(reversed(repo.languages)) else '├'
                print(f"  {border_symbol} {lang_name}: {lang.bbytes}")

    for place in places:
        print(f"\nHandling {place}:")
        repos = deepcopy(default_repos)

        # Include forks
        if not place.include_forks:
            repos = [repo for repo in repos if not repo.fork]

        # Include collaborative
        if not place.include_collaborative:
            repos = [repo for repo in repos if not repo.collaborative]

        # Replace
        for repo in repos:
            for replace_from, replace_to in place.replace.items():
                if ':' in replace_from:
                    replace_from_repo, replace_from = replace_from.split(':')
                    if repo.name != replace_from_repo:
                        continue

                if replace_from in repo.languages:
                    if replace_to not in repo.languages:
                        repo.languages[replace_to] = Lang(replace_to, 0)
                    repo.languages[replace_to].bbytes += repo.languages.pop(replace_from).bbytes

        # Hide
        for repo in repos:
            for lang_name in list(repo.languages.keys()):
                if (repo.name, lang_name) in place.hide or lang_name in place.hide:
                    del repo.languages[lang_name]

        languages = {}
        for repo in repos:
            for lang_name, lang in repo.languages.items():
                if lang_name not in languages:
                    languages[lang_name] = Lang(lang_name, 0)
                languages[lang_name].bbytes += lang.bbytes
        languages = list(languages.values())

        total_bytes = sum(lang.bbytes for lang in languages)

        if LOG:
            print(f"──┤ Total bytes of code: {print_bytes(total_bytes)} ├──")
            for lang in sorted(languages, key=lambda item: -item.bbytes):
                print(f"{lang.name}: {print_bytes(lang.bbytes)} = {round(lang.bbytes * 100 / total_bytes, 2)}%")

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
    if len(sys.argv) == 4:
        process_readme(*sys.argv[1:])
    else:
        print("─── Not enough or too much arguments passed, running debug/dev mode ───\n")
        process_readme("../npanuhin/README.md", "npanuhin/npanuhin", True)

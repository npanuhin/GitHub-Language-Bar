from collections.abc import Iterable
# import json

from yaml import safe_load as yaml_load
from requests import Session, get as req_get


linguist_data = req_get("https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml").text
GITHUB_COLORS = {
    name: lang_data.get("color")
    for name, lang_data in yaml_load(linguist_data).items()
}
LANGUAGE_ALIASES = {}
for name, lang_data in yaml_load(linguist_data).items():
    GITHUB_COLORS[name] = lang_data.get("color")
    LANGUAGE_ALIASES[name] = name
    for alias in lang_data.get("aliases", ()):
        LANGUAGE_ALIASES[alias] = name


class GitHub:
    def __init__(self, gh_token=None, username=None, only_public=False):
        self.only_public = only_public
        self.username = username
        self.gh_token = gh_token
        self.session = Session()
        self.session.headers.update({
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json"
        })

    # def get_my_username(self) -> str:
    #     response = self.session.get("https://api.github.com/user")
    #     assert response.status_code == 200, f"Can't fetch user info ({response.status_code}):\n{response.text}"
    #     return response.json()["login"]

    def get_my_repos(self) -> Iterable[dict]:
        if self.only_public:
            api_url = f"https://api.github.com/users/{self.username}/repos"
            self.session.headers.pop("Authorization", None)
        else:
            self.session.headers["Authorization"] = f"Bearer {self.gh_token}"
            api_url = "https://api.github.com/user/repos"

        page = 0
        while page is not None:
            response = self.session.get(api_url, params={
                "affiliation": "owner",
                "per_page": 100,
                "page": page
            })
            assert response.status_code == 200, \
                f"Can't fetch user repositories ({response.status_code}):\n{response.text}"

            if "Link" in response.headers:
                for item in response.headers["Link"].split(", "):
                    if item.split("; ")[1].strip() == 'rel="next"':
                        page += 1
                        break
                else:
                    page = None
            else:
                page = None

            # with open("output/repos.json", 'w', encoding="utf-8") as file:
            #     json.dump(response.json(), file, ensure_ascii=False, indent=4)
            # with open("output/headers.json", 'w', encoding="utf-8") as file:
            #     json.dump(dict(response.headers), file, ensure_ascii=False, indent=4)

            yield from response.json()

    def get_repo_languages(self, repo_name: str) -> dict[str, int]:
        response = self.session.get(f"https://api.github.com/repos/{repo_name}/languages")
        assert response.status_code == 200, \
            f"Can't fetch repository languages ({response.status_code}):\n{response.text}"
        return response.json()


if __name__ == "__main__":  # Development & manual testing
    import os
    os.chdir("../")

    # with open(".gh_token", encoding="utf-8") as file:
    #     GH_TOKEN = file.read().strip()
    # GITHUB = GitHub(GH_TOKEN)

    GITHUB = GitHub(username="npanuhin", only_public=True)

    print(list(GITHUB.get_my_repos()))

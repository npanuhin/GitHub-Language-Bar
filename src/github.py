from collections.abc import Iterable
# import json

from requests import Session


class GitHub:
    def __init__(self, gh_token):
        self.session = Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {gh_token}"
        })

    def get_my_repos(self) -> Iterable[int]:
        page = 0
        while page is not None:
            response = self.session.get("https://api.github.com/user/repos", params={
                "affiliation": "owner",
                "per_page": 100,
                "page": page
            })
            assert response.status_code == 200, "Can't fetch user repositories:\n" + response.text

            if "Link" in response.headers:
                for item in response.headers["Link"].split(", "):
                    if item.split("; ")[1].strip() == 'rel="next"':
                        page += 1
                        break
                else:
                    page = None
            else:
                page = None

            # with open("headers.debug.json", 'w', encoding="utf-8") as file:
            #     json.dump(dict(response.headers), file, ensure_ascii=False, indent=4)

            yield from response.json()

    def get_repo_languages(self, repo_full_name: str) -> dict[str, int]:
        response = self.session.get(f"https://api.github.com/repos/{repo_full_name}/languages")
        assert response.status_code == 200, "Can't fetch repository languages:\n" + response.text
        # print(f"Languages for {repo_full_name}:")
        # print(response.json())
        return response.json()

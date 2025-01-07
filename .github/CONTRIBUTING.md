<h1 align="center">Contributing</h1>

Python version: 3.12 (for linting, e.g. flake8)

#### Code linting

```bash
pip install -r ".github/flake8.requirements.txt"
flake8 --show-source --statistics

```
<!-- ```bash
# To install pre-commit hook:
pip install -U pre-commit
pre-commit install --config ".github/.pre-commit-config.yaml"
``` -->

#### Access token

Generate and place your token in `/.gh_token` file (~~or use the `GH_TOKEN` environmental variable~~)

#### TODO List

- [ ] Check "Works only when private repositories are enabled"
- [ ] Check logging and write about it in README
- [ ] Check "Not a **contributor** — **collaborator**! I can not count contributions yet("
- [ ] Better options documentation
- [ ] Image?
- [ ] Check "Actually, it should be on a separate line"
- [ ] Check path to README.md, white about it in README, add link from the first step to the docs

- [x] ~~Convert `Jupyter Notebook` to `Python` with some coefficient (like 0.1), or maybe even parse it~~ \[Can't parse because it's too compicated.
We need to retrive file tree (which we can't do if there are too many files or if they are larger than 100 MB). And I don't know, just `master` branch or all existing\]
- [x] Option to hide unwanted languages
- [x] Maybe exclude certain languages from the repositories individually (`exclude=repo.language`)?
- [x] Somehow log per-repository language usage for private repositories without showing them ¯\\\_(ツ)\_/¯
- [x] Affiliation `owner`/`all`
- [x] ~~Different styles for dark and light mode~~ \[*Won't be implemented yet as I don't see the need, gray works well for both light and dark mode*\]
- [x] Replace `repo:language`
- [ ] Add a title
- [ ] Replace (modify) with formula: `Langbar?replace= C++ -> 0.9 * ({C++} - 100)`. For example, for competitive programming, when you have a constant amount of code at the beginning of each file
- [ ] Option to remove promotion URL (possibly if the user has given the project a star xd)
- [ ] Changeable text color (white/grey/etc) + light/dark mode themes


# [License: MIT](https://npanuhin.me/LICENSE)

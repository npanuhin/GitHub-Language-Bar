<h1 align="center">Contributing</h1>

#### Code linting
```bash
pip install -U -r ".github/flake8.requirements.txt"
flake8 --show-source --statistics

# To install pre-commit hook:
pip install -U pre-commit
pre-commit install --config ".github/.pre-commit-config.yaml"
```

#### Access token
Generate and place your token in `/.gh_token` file (~~or use the `GH_TOKEN` environmental variable~~)

#### TODO List
- [x] ~~Convert `Jupyter Notebook` to `Python` with some coefficient (like 0.1), or maybe even parse it~~ \[Can't parse because it's too compicated.
We need to retrive file tree (which we can't do if there are too many files or if they are larger than 100 MB). And I don't know, just `master` branch or all existing\]
- [x] Option to hide unwanted languages
- [x] Maybe exclude certain languages from the repositories individually (`exclude=repo.language`)?
- [x] Somehow log per-repository language usage for private repositories without showing them ¯\\\_(ツ)\_/¯
- [x] Affiliation `owner`/`all`
- [x] ~~Different styles for dark and light mode~~ \[*Won't be implemented yet as I don't see the need, gray works well for both light and dark mode*\]
- [x] Replace `repo:language`
- [ ] Add a title

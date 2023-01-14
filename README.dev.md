<h1 align="center">GitHub Language Bar</h1>

<img src="https://raw.githubusercontent.com/npanuhin/npanuhin/language-bar/bar.svg" width="100%">

## Features

TODO

<!-- - Hosted on github actions. No 3rd party servers (like Heroku) required. Is GitHub working?<sup>\[?\]</sup> Yes? Than ...
- Includes private repositories (because you can specify GITHUB_TOKEN)*

But is does not spam you with commits! Only one commit on a separate branch you will never have to worry about

It's worth mentioning [github-readme-stats](https://github.com/anuraghazra/github-readme-stats#language-card-exclusive-options), in whitch I didn't find all of the listed fetures -->

## Wanna add one to you profile?

> Just two steps, two minutes! ⏱

1. Create a workflow file named `language_bar.yml` in your repository under `.github/workflows` folder and paste the following content inside. [Here is an example](https://github.com/npanuhin/GitHub-Language-Bar/blob/master/.github/workflows/language_bar.yml)
    ```YAML
    name: GitHub Language Bar

    on:
      push:                     # Run every time config or README changes
        paths:
          - 'README.md'
          - '.github/workflows/language_bar.yml'
      schedule:                 # Run every day close to 00:00
        - cron: '50 23 * * *'
      workflow_dispatch:        # Run with a button in the Actions tab

    jobs:
      language_bar:
        name: Create GitHub Language Bar
        runs-on: ubuntu-latest
        steps:
          - name: Create Language Bar
            uses: npanuhin/GitHub-Language-Bar@master
    ```

2. Add this mark anywhere in your README[^anywhere_in_readme]:
    ```html
    <!-- Langbar -->
    ```
3. . . . There is no 3rd step, you are all set! Your bar should appear in a few seconds.<br>
    
    The next steps are optional, but I suggest [enabling private repositories](#enable-private-repositories) so that people can see your true language usage across all of your repositories, not just the public ones.
    
    You can also [customize](#Customize) your new language bar in various ways. If you have any questions, [don't hesitate to ask](https://github.com/npanuhin/GitHub-Language-Bar/issues/new)!

## Enable private repositories

1. Generate a new **repo**-scoped personal access token:
    - Go to https://github.com/settings/tokens/new
    - Name the token as you like, e.g. `Language-Bar-token`
    - Set `Expiration` date to `No Expiration`
    - Click on the first checkbox named `repo`
    - `Generate token` down below
    - Finally, copy your new token to your clipboard

    <details>
    <summary>Help me find these buttons!</summary>

    ![](assets/GLB-tutorial-token.png)
    </details>

2. Add this token to your repository:
    - Go to your repository settings, then (on the left side) `Secrets and Variables` -> `Actions`
    - Click on `New repository secret`
    - Name it `LANG_BAR_PAT`
    - Paste the copied token into the `secret` textarea
    - Hit `Add secret`

    <details>
    <summary>Help me find these buttons!</summary>

    ![](assets/GLB-tutorial-token-2.png)
    </details>


3. Add the following parameter to your workflow file `.github/workflows/language_bar.yml`:
    ```DIFF
        uses: npanuhin/GitHub-Language-Bar@master
    +   with:               # Token is used to fetch private repositories
    +     gh_token: ${{ secrets.LANG_BAR_PAT }}
    ```
    <details>
    <summary>All together it should look like this</summary>

    ```YAML
    name: GitHub Language Bar

    on:
      push:                     # Run every time config or README changes
        paths:
          - 'README.md'
          - '.github/workflows/language_bar.yml'
      schedule:                 # Run every day close to 00:00
        - cron: '50 23 * * *'
      workflow_dispatch:        # Run with a button in the Actions tab

    jobs:
      language_bar:
        name: Create GitHub Language Bar
        runs-on: ubuntu-latest
        steps:
          - name: Create Language Bar
            uses: npanuhin/GitHub-Language-Bar@master
            with:               # Token is used to fetch private repositories
              gh_token: ${{ secrets.LANG_BAR_PAT }}
    ```
    </details>

> **Warning**<br>
> If you enable private repositories, the script will collect and log some information about them. Since your profile repository is almost always public, everyone can see your workflow logs. Here is a list of what others might see and learn about your private repositories:
> - Total bytes of code in your GitHub repositories (including public ones)

## Customize

TODO

<!-- query with multiple keys params -->
<!-- replacements -->


## Development

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
- Convert `Jupyter Notebook` to `Python` with some coefficient (like 0.1), or maybe even parse it
- Hide unwanted languages option (show them as "others")
- Maybe exclude certain languages from the repositories individually (`exclude=repo.language`)?
- Somehow log per-repository language usage for private repositories without showing them ¯\\\_(ツ)\_/¯
- Type `owner`/`all`
- ~~Different styles for dark and light mode~~ \[*Won't be implemented yet as I don't see the need, gray works well for both light and dark mode*\]


[^anywhere_in_readme]: Actually, it should be at the beginning of the line

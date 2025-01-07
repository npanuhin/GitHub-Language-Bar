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

<!-- 1. Create a workflow file named `language_bar.yml` in your repository under `.github/workflows` folder and paste the following content inside. [Here is an example](https://github.com/npanuhin/GitHub-Language-Bar/blob/master/.github/workflows/language_bar.yml) -->
1. Go to your repository and create a workflow file named `language_bar.yml` under `.github/workflows` folder. Paste the following content inside:
    ```YAML
    name: GitHub Language Bar

    on:
      push:               # Run every time config or README changes
        paths:
          - README.md
          - .github/workflows/*
      schedule:           # Run every day at to 4:38 AM
        - cron: 38 4 * * *
      workflow_dispatch:  # Run with a button in the Actions tab

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
3. You are all set! Your bar should appear in a few seconds.<br>

    The next steps are optional, but I suggest [enabling private repositories](#enable-private-repositories) so that people can see your true language usage across all repositories, not just the public ones.

    You can also [customize](#Customize) your new language bar in various ways. If you have any questions, [don't hesitate to ask!](https://github.com/npanuhin/GitHub-Language-Bar/issues/new)


## Enable private repositories

1. Generate a new personal access token with access to all your current and future repositories:
    - Go to https://github.com/settings/personal-access-tokens/new and fill the following fields:
    - **Token name:** whatever you like, e.g. `Language-Bar-token`
    - **Expiration:** `No Expiration` ⚠
    <!-- - Set the maximum `Expiration` date allowed by GitHub<sup>Once the token expires, you will need to regenerate it<a href="#user-content-fn-fine_grained_token">awd</a></sup> -->

    <!-- - Click on the first checkbox named `repo` -->
    - **Repository access:** `All repositories` ⚠
    - **Permissions:** open up `Repository permissions`:
        - **Contents:** set to `Read-only`
        - **Metadata:** set to `Read-only`
    - Scroll all the way down and click `Generate token`
    - Finally, copy the generated token to the clipboard

    <!-- <details>
    <summary>Help me find these buttons!</summary>

    ![](assets/GLB-tutorial-token.png)
    </details> -->

2. Add this token to your repository:
    1. Go to the repository, where the target `README.md` file is located
    2. Open up the repository settings
    3. On the left side select `Secrets and Variables` -> `Actions`
    4. Click on `New repository secret`
        - **Name:** exactly `LANG_BAR_PAT`
        - **Secret:** Paste the copied in the previous step token from the clipboard
        - Click `Add secret`

    <!-- <details>
    <summary>Help me find these buttons!</summary>

    ![](assets/GLB-tutorial-token-2.png)
    </details> -->


3. <a id="private_enable_lines"></a>Add the following parameter to the workflow file (`.github/workflows/language_bar.yml`):
    ```DIFF
    steps:
      - name: Create Language Bar
        uses: npanuhin/GitHub-Language-Bar@master
    +   with:
    +     gh_token: ${{ secrets.LANG_BAR_PAT }}  # Token is used to fetch private repositories
    ```
    <details>
    <summary>All together it should look like this</summary>

    ```YAML
    name: GitHub Language Bar

    on:
      push:               # Run every time config or README changes
        paths:
          - README.md
          - .github/workflows/*
      schedule:           # Run every day at to 4:38 AM
        - cron: 38 4 * * *
      workflow_dispatch:  # Run with a button in the Actions tab

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

<!-- TODO -->
> [!WARNING]
> If you enable private repositories, the script will collect and log some information about them. Since your profile repository is almost always public, everyone can see your README source and workflow logs (Actions tab). **By default, apart from the bar itself, others cannot learn anything about your private repositories.** However, be careful when using additional settings:
> - <a id="privacy_log_warning"></a>*If [log is turned on](#log)*: number of bytes per language for each repository is logged
> - *If you use [`replace`](#replace_setting) or [`hide`](#hide_setting) options* in the `repo:lang` format, be aware that the repository name is visible to everyone. All [settings](#customize) are also logged. However, logs can be deleted from the Actions tab (be aware of scheduled runs)

> [!NOTE]
> To disable private repositories, just remove or comment out [the added lines](#user-content-private_enable_lines)


## Customize

Customizing GitHub Language Bar is simple — just add the parameter you want after `?`, as if it was a url: `Langbar?key=param`

- **Include forks: `include_forks = yes/no`[^treating_yes_no] (default: `no`)**

    Whether to include [forked](https://git-scm.com/book/en/v2/GitHub-Contributing-to-a-Project) repositories or not

    Example: `<!-- Langbar?include_forks=yes -->`

- **Include collaborative repositories: `include_collaborative = yes/no`[^treating_yes_no] (default/recommended: `no`)**

    Whether to include repositories that you don't own but have access to as a **collaborator**. Works only when [private repositories are enabled](#enable-private-repositories)

    Example: `<!-- Langbar?include_collaborative=yes -->`

    > $${\color{ProcessBlue}ⓘ\ \text{Note}}$$<br>
    > Not a **contributor** — **collaborator**! I can not count contributions yet(

- <a id="replace_setting"></a>**Replace language: `replace=language1->language1_new,repo2:language2->language2_new`**

    Option to replace the desired language with another language in all repositories or only in a specific repository (comma-separated list)

    Example: `<!-- Langbar?replace=Hack->PHP,npanuhin/MyRepo:Hack->PHP -->`

- <a id="hide_setting"></a>**Hide language: `hide=language1,repo2:language2,language3`**

    Option to hide the desired language in all repositories or only in a specific repository (comma-separated list)

    <a id="hide_setting_example"></a>Example: `<!-- Langbar?hide=Jupyter Notebook,npanuhin/MyRepo:JavaScript -->`

<!-- TODO -->
<!-- - <a id="hide_setting"></a>**Image link: `link={some url}`**

    Option to hide the desired language in all repositories or only in a specific repository (comma-separated list)

    <a id="hide_setting_example"></a>Example: ` --><!-- Langbar?hide=Jupyter Notebook,npanuhin/MyRepo:JavaScript -->`

Example of all settings combined:  <!-- TODO -->
```
<!-- Langbar?include_forks=yes&include_collaborative=yes&hide=Jupyter Notebook,npanuhin/MyRepo:JavaScript -->
```

> [!NOTE]
> Settings are applied in the order they appear in this list. For example, `hide` is always applied after `replace`


## Logging

If you want to see the number of bytes of each language in each repository (to get an idea of which setting is best to apply) <!-- TODO language -->, you can use the `log` parameter.
[Be mindful of your privacy!](#privacy_log_warning)

```DIFF
steps:
  - name: Create Language Bar
    uses: npanuhin/GitHub-Language-Bar@master
+   with:
+     log: true
```

After the GitHub Action completes, the log will be at `{your_repo_url}/blob/language-bar/log.txt`.<br>
For example: https://github.com/npanuhin/npanuhin/blob/language-bar/log.txt


## Pro tips

1. As in URLs, individual settings can be used multiple times. For example:<br>
    `<!-- Langbar?hide=Jupyter Notebook&hide=npanuhin/MyRepo:JavaScript -->`<br>
    is equal to [the previous `hide` example](#hide_setting_example)

2. If you want to add a bar to a file other than `/README.md`, you can specify its path in the `readme_path` parameter (without leading slash):
    ```DIFF
        steps:
      - name: Create Language Bar
        uses: npanuhin/GitHub-Language-Bar@master
    +   with:
    +     readme_path: 'path/to/my/awesome/README.md'
    ```

## Contributing

For technical details and TODO list see [contribution guide](.github/CONTRIBUTING.md)


[^anywhere_in_readme]: Actually, it should be on a separate line
[^treating_yes_no]: `YeS`, `1`, `true`, `on`, etc. are treated as `yes`, otherwise as `no`
<!-- [^fine_grained_token]: For some reason, GitHub [has made it impossible](https://github.blog/2022-10-18-introducing-fine-grained-personal-access-tokens-for-github/#fine-grained-personal-access-tokens-in-action) to create applications like GitHub Language Bar that need all-time access to all repositories — either you can't access repositories in organizations that have disabled classic tokens, or you need to reissue a fine-grained token every year
 -->
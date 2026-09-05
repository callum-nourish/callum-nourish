from gifos import Terminal
from gifos.utils import fetch_github_stats
from datetime import datetime
from zoneinfo import ZoneInfo
from random import randint
from collections import Counter
import os
import requests

USERNAME = "callum-nourish"
"""GitHub username"""

EXPERIENCE = [ "Nourish Care" ]
"""Work experience"""

FOCUS = [ "Ruby on Rails", "Vue", "Postgres", "AWS/DynamoDB" ]
"""Areas of focus"""

INTERESTS = [ "AI/ML", "Databases", "Electronics", "Terminal Tooling" ]
"""Areas of interest"""

ROLE = "Software Engineer"
"""Current role"""

ZONE = ZoneInfo("Europe/London")
"""Timezone"""

INFO_DISPLAY_TIME = 500
"""How long the info section is displayed"""

WIDTH = 750
"""Terminal width"""

HEIGHT = 500
"""Terminal height"""

PADDING = 15
"""Terminal padding"""

FONT_SIZE = 16
"""Terminal font size"""

SPEED = 1
"""Typing speed"""

COUNT = 5
"""Number of times to generate text"""

VERSION = "1.0.0"
"""Version of the script"""

GIT_COMMIT_MESSAGE = "AI rubber duck said it looked fine"
"""Git commit message"""

EXCLUDE_LANGUAGES = { "HTML", "CSS", "Dockerfile", "Shell", "Makefile", "Batchfile", "QML" }
"""Markup/config languages that pad the language list without reflecting real stack choices"""

def fetch_languages_by_repo_count(username: str) -> list[tuple[str, float]]:
    """
    Fetches top languages weighted by number of repos they appear in, rather than
    total bytes written — a couple of repos with generated/vendored HTML otherwise
    dwarf everything else under byte-size weighting.

    Args:
        username (str): GitHub username

    Returns:
        list[tuple[str, float]]: language name, percentage of repos it appears in, sorted desc
    """
    repo_counts = Counter()
    total_repos = 0
    cursor = None

    query = """
    query($username: String!, $cursor: String) {
        user(login: $username) {
            repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
                nodes {
                    isFork
                    languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
                        nodes { name }
                    }
                }
                pageInfo { endCursor hasNextPage }
            }
        }
    }
    """
    headers = { "Authorization": f"bearer {os.getenv('GITHUB_TOKEN')}" }

    while True:
        response = requests.post(
            "https://api.github.com/graphql",
            json = { "query": query, "variables": { "username": username, "cursor": cursor } },
            headers = headers,
        )
        page = response.json()["data"]["user"]["repositories"]

        for repo in page["nodes"]:
            if repo["isFork"]:
                continue
            total_repos += 1
            for language in { node["name"] for node in repo["languages"]["nodes"] } - EXCLUDE_LANGUAGES:
                repo_counts[language] += 1

        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    return [
        (language, round(count / total_repos * 100, 2))
        for language, count in repo_counts.most_common()
    ]

USER_DETAILS = fetch_github_stats(USERNAME, include_all_commits = True)
"""User details fetched from GitHub, including stats like followers, stars, commits, languages, etc."""

USER_DETAILS.languages_sorted = fetch_languages_by_repo_count(USERNAME)
"""Overrides byte-size-weighted languages with repo-count-weighted ones (see docstring above)."""

def red(text: str | int) -> str:
    return f"\x1b[31m{text}\x1b[0m"

def green(text: str | int) -> str:
    return f"\x1b[32m{text}\x1b[0m"

def yellow(text: str | int) -> str:
    return f"\x1b[33m{text}\x1b[0m"

def blue(text: str | int) -> str:
    return f"\x1b[34m{text}\x1b[0m"

def magenta(text: str | int) -> str:
    return f"\x1b[35m{text}\x1b[0m"

def cyan(text: str | int) -> str:
    return f"\x1b[36m{text}\x1b[0m"

def bright_red(text: str | int) -> str:
    return f"\x1b[91m{text}\x1b[0m"

def bright_magenta(text: str | int) -> str:
    return f"\x1b[95m{text}\x1b[0m"

def format_list(items: list[str]) -> str:
    return (" · ").join(items)

def list_languages() -> list[str]:
    languages = [ ]

    for language, percent in USER_DETAILS.languages_sorted:
        if language == "Jupyter Notebook": language = "Jupyter"

        lang = f"{bright_magenta(language)} ({yellow(f'{percent}%')})"
        languages.append(lang)

    return languages

def profile_details() -> str:
    top_languages = list_languages()

    return f"""
{magenta(f"User Profile")}
--------------
{bright_magenta("Role")}:           {yellow(ROLE)}
{bright_magenta("Experience")}:     {format_list([yellow(experience) for experience in EXPERIENCE])}
{bright_magenta("Focus")}:          {format_list([yellow(focus) for focus in FOCUS])}
{bright_magenta("Interests")}:      {format_list([yellow(interest) for interest in INTERESTS])}

{magenta("GitHub Stats")}
--------------
{bright_magenta("Total Stars")}:    {yellow(USER_DETAILS.total_stargazers)}
{bright_magenta("Total Commits")}:  {yellow(USER_DETAILS.total_commits_all_time)}
{bright_magenta("Pull Requests")}:  {yellow(USER_DETAILS.total_pull_requests_made)}
{bright_magenta("Contributions")}:  {yellow(USER_DETAILS.total_repo_contributions)}

{magenta("Top Languages")}
--------------
{format_list(top_languages[:5])}
{format_list(top_languages[5:10])}
    """

def login(t: Terminal):
    t.toggle_show_cursor(False)
    t.gen_text(bright_red(f"{USERNAME.upper()} v{VERSION}"), t.curr_row, count = COUNT)

    t.curr_row += 2

    t.gen_text("login: ", t.curr_row, count = COUNT)
    t.toggle_show_cursor(True)
    t.gen_typing_text(USERNAME, t.curr_row, speed = SPEED, contin = True)
    t.toggle_show_cursor(False)

    t.curr_row += 1

    t.gen_text("password: ", t.curr_row, count = COUNT)
    t.toggle_show_cursor(True)
    t.gen_typing_text("*******", t.curr_row, speed = SPEED, contin = True)
    t.toggle_show_cursor(False)

    t.curr_row += 2

    time_now = datetime.now(ZONE).strftime("%a %b %d %H:%M:%S")
    t.gen_text(f"Last login: {time_now} on {f"tty00{randint(0, 9)}"}", t.curr_row)

def clear(t: Terminal):
    t.curr_row += 1

    t.set_prompt(f"{cyan(USERNAME)}@{green('localhost:')}{red('~')}$ ")
    t.gen_prompt(t.curr_row, count = COUNT)

    t.toggle_show_cursor(True)
    t.gen_typing_text(blue("clear"), t.curr_row, speed = SPEED, contin = True)

    t.clear_frame()

def fetch(t: Terminal):
    t.gen_prompt(t.curr_row, count = COUNT)

    t.gen_typing_text(blue("fetch.sh"), t.curr_row, contin = True, speed = SPEED)

    prompt_col = t.curr_col
    t.gen_typing_text(cyan(" -"), t.curr_row, contin = True, speed = SPEED)
    t.delete_row(t.curr_row, prompt_col)
    t.gen_text(bright_red(" -u"), t.curr_row, count = 3, contin = True)

    t.gen_typing_text(f" {cyan(USERNAME)}", t.curr_row, speed = SPEED, contin = True)

def info(t: Terminal):
    t.curr_row += 1
    t.gen_text(profile_details(), t.curr_row)

def final(t: Terminal):
    t.gen_prompt(t.curr_row, count = COUNT)

    t.gen_typing_text(blue("git"), t.curr_row, contin = True, speed = SPEED)
    t.gen_typing_text(cyan(" commit"), t.curr_row, contin = True, speed = SPEED)

    prompt_col = t.curr_col
    t.gen_typing_text(cyan(" -"), t.curr_row, contin = True, speed = SPEED)
    t.delete_row(t.curr_row, prompt_col)
    t.gen_text(bright_red(" -a"), t.curr_row, contin = True)
    t.gen_typing_text(bright_red("m"), t.curr_row, speed = SPEED, contin = True)

    t.gen_typing_text(cyan(f" \"{GIT_COMMIT_MESSAGE}\""), t.curr_row, contin = True, speed = SPEED)
    t.gen_text("", t.curr_row, count = INFO_DISPLAY_TIME, contin = True)

def main():
    t = Terminal(width = WIDTH,
                 height = HEIGHT,
                 xpad = PADDING,
                 ypad = PADDING,
                 font_size = FONT_SIZE)

    login(t)
    clear(t)
    fetch(t)
    info(t)
    final(t)

    t.gen_gif()

if __name__ == "__main__":
    main()

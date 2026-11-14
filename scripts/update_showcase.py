"""Rebuild the project list in README.md.

Lists every public repo owned by OWNER that has the topic TOPIC.
To show a new project on the profile, add the topic to that repo.
"""

import json
import os
import pathlib
import urllib.request

OWNER = "varun1505"
TOPIC = "showcase"
START = "<!-- showcase:start -->"
END = "<!-- showcase:end -->"
README = pathlib.Path(__file__).resolve().parent.parent / "README.md"


def fetch_repos():
    url = (
        "https://api.github.com/search/repositories"
        f"?q=user:{OWNER}+topic:{TOPIC}+fork:true&per_page=100"
    )
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        repos = json.load(response)["items"]
    # Most stars first. Newest push breaks a tie.
    repos.sort(key=lambda r: (r["stargazers_count"], r["pushed_at"]), reverse=True)
    return repos


def render(repos):
    lines = []
    for repo in repos:
        line = f"- **[{repo['name']}]({repo['html_url']})**"
        if repo["stargazers_count"]:
            line += f" ★ {repo['stargazers_count']}"
        if repo["description"]:
            line += f"<br>{repo['description'].strip()}"
        lines.append(line)
    return "\n".join(lines)


def main():
    repos = fetch_repos()
    if not repos:
        # An empty result is more likely an API problem than a real change.
        raise SystemExit(f"No repos found with topic '{TOPIC}'. README left as it is.")
    text = README.read_text()
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(f"{before}{START}\n{render(repos)}\n{END}{after}")
    print(f"Listed {len(repos)} repos.")


if __name__ == "__main__":
    main()

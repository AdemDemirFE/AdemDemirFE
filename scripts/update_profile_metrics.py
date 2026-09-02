import json, os, urllib.request
from collections import Counter
from datetime import datetime

USER = os.environ.get("GH_USER", "AdemDemirFE")
TOKEN = os.environ["GH_TOKEN"]
API = "https://api.github.com"


def rest(path):
    req = urllib.request.Request(
        API + path,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AdemDemirFE-profile-metrics",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "AdemDemirFE-profile-metrics",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


def fmt(n):
    return f"{n:,}".replace(",", " ")

repos = []
page = 1
while True:
    batch = rest(f"/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated")
    repos.extend(batch)
    if len(batch) < 100:
        break
    page += 1

stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
langs = Counter()
for repo in repos:
    try:
        data = rest(repo["languages_url"].replace(API, ""))
        for name, value in data.items():
            langs[name] += value
    except Exception:
        continue

query = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""
cc = graphql(query, {"login": USER})["user"]["contributionsCollection"]
days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
days.sort(key=lambda x: x["date"])

current = 0
for d in reversed(days):
    if d["contributionCount"] > 0:
        current += 1
    else:
        break

longest = 0
run = 0
for d in days:
    if d["contributionCount"] > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0

rows = [
    ("⭐ Stars received", fmt(stars)),
    ("🍴 Forks", fmt(forks)),
    ("📦 Public repositories", fmt(len(repos))),
    ("📝 Commits", fmt(cc["totalCommitContributions"])),
    ("🔀 Pull requests", fmt(cc["totalPullRequestContributions"])),
    ("🐛 Issues", fmt(cc["totalIssueContributions"])),
    ("👀 PR reviews", fmt(cc["totalPullRequestReviewContributions"])),
    ("🔥 Current contribution streak", f"{current} days"),
    ("🏆 Longest contribution streak", f"{longest} days"),
    ("📈 Contributions in current period", fmt(cc["contributionCalendar"]["totalContributions"])),
]

lines = ["| Metric | Value |", "|---|---:|"]
lines += [f"| {a} | **{b}** |" for a, b in rows]

lines += ["", "### 💻 Most Used Languages", ""]
total = sum(langs.values()) or 1
for name, value in langs.most_common(8):
    pct = value / total * 100
    blocks = max(1, round(pct / 5))
    lines.append(f"- **{name}** `{pct:.1f}%` `{'█' * blocks}{'░' * (20 - blocks)}`")
if not langs:
    lines.append("`Language data temporarily unavailable.`")

lines += ["", "### 📅 Recent Contribution Activity", ""]
weekly = []
for week in cc["contributionCalendar"]["weeks"][-12:]:
    total_week = sum(d["contributionCount"] for d in week["contributionDays"])
    start = week["contributionDays"][0]["date"]
    weekly.append((start, total_week))
for start, value in weekly:
    label = datetime.fromisoformat(start).strftime("%d %b")
    blocks = min(20, max(1, value // max(1, max(v for _, v in weekly) // 20 or 1))) if value else 0
    bar = "█" * blocks + "░" * (20 - blocks)
    lines.append(f"- `{label}` `{bar}` **{value}** contributions")

new_block = "<!-- PROFILE_METRICS:START -->\n\n" + "\n".join(lines) + "\n\n<!-- PROFILE_METRICS:END -->"

path = "README.md"
text = open(path, encoding="utf-8").read()
start = text.index("<!-- PROFILE_METRICS:START -->")
end = text.index("<!-- PROFILE_METRICS:END -->") + len("<!-- PROFILE_METRICS:END -->")
text = text[:start] + new_block + text[end:]
open(path, "w", encoding="utf-8").write(text)
print("Updated profile metrics for", USER)

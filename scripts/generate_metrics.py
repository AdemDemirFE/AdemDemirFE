import json, os, urllib.request
from datetime import datetime, timedelta, timezone
from collections import Counter

USER = os.environ.get("GH_USER", "AdemDemirFE")
TOKEN = os.environ["GH_TOKEN"]
API = "https://api.github.com"

def get(path):
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-profile-metrics"
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

repos = []
page = 1
while page <= 10:
    batch = get(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
    if not batch: break
    repos.extend(batch)
    if len(batch) < 100: break
    page += 1

profile = get(f"/users/{USER}")
stars = sum(r.get("stargazers_count",0) for r in repos)
forks = sum(r.get("forks_count",0) for r in repos)
languages = Counter()
for r in repos:
    try:
        langs = get(r["languages_url"].replace(API,""))
        for k,v in langs.items(): languages[k] += v
    except Exception:
        pass

# Contribution totals / streak data from GraphQL.
query = """
query($login:String!) {
  user(login:$login) {
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount date }
        }
      }
    }
  }
}
"""
payload = json.dumps({"query":query,"variables":{"login":USER}}).encode()
req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type":"application/json",
    "User-Agent":"github-profile-metrics"
})
with urllib.request.urlopen(req, timeout=30) as r:
    gql = json.load(r)

cc = gql["data"]["user"]["contributionsCollection"]
days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
days.sort(key=lambda x:x["date"])

current = 0
for d in reversed(days):
    if d["contributionCount"] > 0: current += 1
    else: break

longest = 0
run = 0
for d in days:
    if d["contributionCount"] > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0

def write_card(path, title, rows, height=360):
    W=1200
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}">',
         '<rect width="100%" height="100%" rx="24" fill="#0f172a"/>',
         f'<text x="60" y="62" font-family="Arial" font-size="30" font-weight="700" fill="#06b6d4">{esc(title)}</text>']
    y=120
    for label,value in rows:
        out += [
          f'<text x="70" y="{y}" font-family="Arial" font-size="20" fill="#94a3b8">{esc(label)}</text>',
          f'<text x="70" y="{y+42}" font-family="Arial" font-size="34" font-weight="700" fill="#f8fafc">{esc(value)}</text>'
        ]
        y += 105
    out.append('</svg>')
    open(path,"w",encoding="utf-8").write("\n".join(out))

write_card("assets/github-stats.svg","GITHUB ANALYTICS",[
    ("Total contributions (current period)", cc["contributionCalendar"]["totalContributions"]),
    ("Public repositories", len(repos)),
    ("Stars received", stars),
    ("Forks", forks),
    ("Current streak / Longest streak", f"{current} / {longest} days")
],height=620)

top = languages.most_common(8)
total = sum(v for _,v in top) or 1
lang_rows = [(name, f"{value/total*100:.1f}%") for name,value in top]
write_card("assets/top-languages.svg","TOP LANGUAGES",lang_rows,height=max(260, 110+len(lang_rows)*70))

# Activity bars for the latest 12 weeks.
weekly=[]
for w in cc["contributionCalendar"]["weeks"][-12:]:
    totalw=sum(d["contributionCount"] for d in w["contributionDays"])
    weekly.append(totalw)
W=1200; H=420
mx=max(weekly) if weekly else 1
out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
     '<rect width="100%" height="100%" rx="24" fill="#0f172a"/>',
     '<text x="60" y="55" font-family="Arial" font-size="30" font-weight="700" fill="#06b6d4">CONTRIBUTION ACTIVITY • LAST 12 WEEKS</text>']
bar_w=70
for i,v in enumerate(weekly):
    h=max(4,int((v/mx)*260))
    x=80+i*90
    y=340-h
    out += [f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" rx="8" fill="#06b6d4"/>',
            f'<text x="{x+bar_w/2}" y="370" text-anchor="middle" font-family="Arial" font-size="15" fill="#94a3b8">{v}</text>']
out.append('</svg>')
open("assets/activity.svg","w",encoding="utf-8").write("\n".join(out))

write_card("assets/achievements.svg","ENGINEERING SNAPSHOT",[
    ("Commits", cc["totalCommitContributions"]),
    ("Issues", cc["totalIssueContributions"]),
    ("Pull requests", cc["totalPullRequestContributions"]),
    ("PR reviews", cc["totalPullRequestReviewContributions"]),
    ("Public repositories", len(repos))
],height=620)

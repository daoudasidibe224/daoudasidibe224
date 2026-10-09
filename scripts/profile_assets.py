"""Generate the profile's self-hosted SVGs from GitHub's public responses."""
import argparse
import datetime as dt
import html
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER = "daoudasidibe224"


def fetch(url):
    headers = {"User-Agent": "Daouda-profile-assets", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        return response.read().decode()


def parse_calendar(source):
    """Match each dated calendar cell to its own accessible contribution count."""
    tooltips = dict(re.findall(r'<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>(.*?)</tool-tip>', source, re.S))
    days = {}
    for cell in re.findall(r'<td\b[^>]*data-date="[^\"]+"[^>]*>', source):
        date = re.search(r'data-date="([^\"]+)"', cell).group(1)
        key = re.search(r'\bid="([^\"]+)"', cell).group(1)
        text = html.unescape(re.sub(r'<[^>]+>', '', tooltips.get(key, ''))).strip()
        if text.startswith("No contributions"):
            days[date] = 0
        else:
            count = re.match(r'([\d,]+) contributions?\b', text)
            if not count:
                raise ValueError(f"Unreadable GitHub count for {date}")
            days[date] = int(count.group(1).replace(',', ''))
    if not days:
        raise ValueError("GitHub returned no contribution calendar")
    return days


def snapshot(today):
    account = json.loads(fetch(f"https://api.github.com/users/{USER}"))
    days = parse_calendar(fetch(f"https://github.com/users/{USER}/contributions?from={today.year}-01-01&to={today.isoformat()}"))
    expected = [(dt.date(today.year, 1, 1) + dt.timedelta(days=i)).isoformat()
                for i in range((today - dt.date(today.year, 1, 1)).days + 1)]
    # January's first partial week is sometimes absent from GitHub's HTML.
    # Fail rather than turn missing data into fabricated zero contributions.
    missing = [day for day in expected if day not in days]
    source = fetch(f"https://github.com/users/{USER}/contributions?from={today.year}-01-01&to={today.isoformat()}") if missing else None
    year_match = re.search(r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions', source or '')
    if missing and not year_match:
        raise ValueError("Cannot verify the yearly contribution total")
    year_total = int(year_match.group(1).replace(',', '')) if missing else sum(days[day] for day in expected)
    start = max(dt.date(today.year, 1, 1), today - dt.timedelta(days=89))
    recent = []
    for offset in range((today - start).days + 1):
        day = (start + dt.timedelta(days=offset)).isoformat()
        if day not in days:
            raise ValueError(f"Missing calendar day {day}")
        recent.append({"date": day, "count": days[day]})
    return {"updated": today.isoformat(), "public_repositories": account["public_repos"],
            "year": today.year, "year_contributions": year_total, "days": recent}


def svg(width, height, title, body, description=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description)}</desc>{body}</svg>\n')


def banner(theme):
    dark = theme == "dark"
    bg, fg, muted, panel = ("#151c22", "#fff2e2", "#c5b8aa", "#1f2b32") if dark else ("#f6f0e8", "#283039", "#746455", "#e9ded0")
    copper = "#dc9a70" if dark else "#a55c39"
    body = f'''<defs><linearGradient id="wash" x2="1" y2="1"><stop stop-color="{bg}"/><stop offset="1" stop-color="{panel}"/></linearGradient></defs>
    <rect width="1000" height="340" rx="18" fill="url(#wash)"/>
    <path d="M720 -60 C580 50 640 250 870 295 S1110 220 1040 70" fill="none" stroke="{copper}" stroke-width="48" opacity=".13"/>
    <path d="M718 -60 C575 55 630 250 863 297 S1110 220 1040 70" fill="none" stroke="{copper}" stroke-width="1" opacity=".5"/>
    <text x="48" y="56" font-family="monospace" font-size="14" letter-spacing="3" fill="{copper}">DÉVELOPPEMENT WEB</text>
    <text x="45" y="137" font-family="Georgia,serif" font-size="62" fill="{fg}">Daouda Sidibe</text>
    <text x="49" y="178" font-family="Verdana,sans-serif" font-size="21" fill="{muted}">Développeur Full Stack · JavaScript / TypeScript</text>
    <text x="49" y="247" font-family="Verdana,sans-serif" font-size="17" fill="{fg}">Des interfaces claires. Des applications qui fonctionnent.</text>
    <text x="49" y="292" font-family="monospace" font-size="13" fill="{copper}" letter-spacing="1">INTERFACE  /  API  /  TESTS</text>
    <g transform="translate(700 83) rotate(-7 120 95)">
      <rect width="246" height="178" rx="13" fill="{bg}" stroke="{copper}" stroke-opacity=".6"/>
      <path d="M0 34H246" stroke="{copper}" stroke-opacity=".25"/>
      <circle cx="19" cy="17" r="4" fill="{copper}"/><circle cx="34" cy="17" r="4" fill="{muted}" opacity=".5"/><circle cx="49" cy="17" r="4" fill="{muted}" opacity=".3"/>
      <path d="M70 69L43 94l27 25M175 69l27 25-27 25M135 60l-27 68" stroke="{copper}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <path d="M46 151H111M122 151H182" stroke="{muted}" opacity=".4" stroke-width="3" stroke-linecap="round"/>
    </g>'''
    return svg(1000, 340, "Daouda Sidibe — Développeur Full Stack JavaScript et TypeScript", body)


def activity(data, theme):
    dark = theme == "dark"
    bg, fg, muted, border = ("#151c22", "#fff2e2", "#b9ad9f", "#34414a") if dark else ("#f6f0e8", "#283039", "#746455", "#e2d7c9")
    colors = ["#26333b", "#694d3f", "#986947", "#bc855b", "#e7ac7d"] if dark else ["#e7ded2", "#dec0a6", "#c9946c", "#ad7046", "#7b472b"]
    copper = "#dc9a70" if dark else "#a55c39"
    updated = dt.date.fromisoformat(data["updated"]).strftime("%d/%m/%Y")
    body = f'<rect x=".5" y=".5" width="999" height="299" rx="16" fill="{bg}" stroke="{border}"/>'
    body += f'<text x="32" y="42" fill="{copper}" font-family="monospace" font-size="15" letter-spacing="2">ACTIVITÉ GITHUB</text>'
    body += f'<text x="32" y="115" fill="{fg}" font-family="Georgia,serif" font-size="58">{data["year_contributions"]}</text>'
    body += f'<text x="32" y="146" fill="{muted}" font-family="Verdana,sans-serif" font-size="15">contributions en {data["year"]}</text>'
    body += f'<text x="32" y="205" fill="{fg}" font-family="Georgia,serif" font-size="35">{data["public_repositories"]}</text>'
    body += f'<text x="75" y="202" fill="{muted}" font-family="Verdana,sans-serif" font-size="15">dépôts publics</text>'
    body += f'<text x="324" y="68" fill="{fg}" font-family="Verdana,sans-serif" font-size="15">Les {len(data["days"])} derniers jours</text>'
    first = dt.date.fromisoformat(data["days"][0]["date"])
    sunday_offset = (first.weekday() + 1) % 7
    for i, day in enumerate(data["days"]):
        slot = i + sunday_offset
        count = day["count"]
        level = 0 if count == 0 else 1 if count < 5 else 2 if count < 10 else 3 if count < 20 else 4
        x, y = 324 + (slot // 7) * 43, 88 + (slot % 7) * 21
        body += f'<rect x="{x}" y="{y}" width="33" height="16" rx="3" fill="{colors[level]}"><title>{day["date"]} : {count} contributions</title></rect>'
    body += f'<text x="324" y="270" fill="{muted}" font-family="Verdana,sans-serif" font-size="13">Relevé du {updated} · données affichées par GitHub</text>'
    return svg(1000, 300, "Activité GitHub de Daouda Sidibe", body,
               f'{data["year_contributions"]} contributions en {data["year"]}, {data["public_repositories"]} dépôts publics. Mis à jour le {updated}.')


def write_assets(data):
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in ("dark", "light"):
        (assets / f"header-{theme}.svg").write_text(banner(theme))
        (assets / f"activity-{theme}.svg").write_text(activity(data, theme))
    for name, label, width, color in [("portfolio", "Voir mon portfolio ↗", 216, "#a55c39"), ("linkedin", "LinkedIn ↗", 140, "#24586e"), ("email", "Me contacter ↗", 176, "#394e45")]:
        body = f'<rect width="{width}" height="42" rx="7" fill="{color}"/><text x="{width/2}" y="27" text-anchor="middle" font-family="Verdana,sans-serif" font-size="14" fill="#ffffff">{label}</text>'
        (assets / f"{name}.svg").write_text(svg(width, 42, label, body))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Regenerate from the last verified snapshot")
    args = parser.parse_args()
    path = ROOT / "assets/activity.json"
    data = json.loads(path.read_text()) if args.offline else snapshot(dt.datetime.now(dt.timezone.utc).date())
    write_assets(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f'Profile assets generated from GitHub data dated {data["updated"]}')

#!/usr/bin/env python3
"""Validate data/*.toml and write README.md from template.md. Python 3.11+, standard library only.

    python3 build.py          rewrite README.md
    python3 build.py --check  exit 1 if an entry is invalid or README.md is out of date (CI runs this)
"""

import datetime
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent

SECTIONS = {
    "serving": ("🚀", "Serving and inference",
                "Agents that change, configure or build inference engines and serving systems."),
    "training": ("🧠", "Training",
                 "Agents that tune or build training and post-training systems."),
    "compiler": ("🧩", "Compilers",
                 "LLM-guided compiler optimization and compiler-agent co-design, evaluated at graph or model level."),
    "benchmark": ("🧪", "Benchmarks",
                  "Benchmarks and environments that measure LLMs and agents on ML-infrastructure tasks."),
    "method": ("🧭", "General methods with ML-infrastructure results",
               "General LLM-driven optimization methods that report results on ML infrastructure."),
}

REQUIRED = {"title": str, "authors": list, "date": datetime.date, "category": str, "summary": str}
OPTIONAL = {"venue": str, "arxiv": str, "url": str, "code": str, "result": str}


def load(errors):
    entries = []
    for path in sorted((ROOT / "data").glob("*.toml")):
        where = path.relative_to(ROOT)
        try:
            entry = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{where}: {exc}")
            continue
        for key in REQUIRED:
            if key not in entry:
                errors.append(f"{where}: missing '{key}'")
        for key, value in entry.items():
            kind = REQUIRED.get(key) or OPTIONAL.get(key)
            if kind is None:
                errors.append(f"{where}: unknown field '{key}'")
            elif not isinstance(value, kind):
                errors.append(f"{where}: '{key}' should be {kind.__name__}")
        if entry.get("category") not in SECTIONS:
            errors.append(f"{where}: 'category' must be one of {', '.join(SECTIONS)}")
        if not entry.get("arxiv") and not entry.get("url"):
            errors.append(f"{where}: needs 'arxiv' or 'url'")
        for key in ("url", "code"):
            if isinstance(entry.get(key), str) and not entry[key].startswith("https://"):
                errors.append(f"{where}: '{key}' must start with https://")
        entry["id"] = path.stem
        entries.append(entry)
    seen = {}
    for entry in entries:
        key = entry.get("arxiv") or entry.get("url")
        if key in seen:
            errors.append(f"data/{entry['id']}.toml duplicates data/{seen[key]}.toml")
        seen[key] = entry["id"]
    entries.sort(key=lambda e: (str(e.get("date", "")), e["id"]), reverse=True)
    return entries


def shield_text(text):
    """Escape text for a static shields.io badge path."""
    return quote(text.replace("-", "--").replace("_", "__"), safe="")


def badges(e):
    out = []
    if e.get("arxiv"):
        out.append(f"[![arXiv](https://img.shields.io/badge/arXiv-{shield_text(e['arxiv'])}-b31b1b?logo=arxiv&logoColor=white)]"
                   f"(https://arxiv.org/abs/{e['arxiv']})")
    if e.get("url"):
        host = urlparse(e["url"]).netloc.removeprefix("www.")
        out.append(f"[![link](https://img.shields.io/badge/link-{shield_text(host)}-0969da)]({e['url']})")
    if e.get("code"):
        parsed = urlparse(e["code"])
        parts = [p for p in parsed.path.split("/") if p]
        if parsed.netloc == "github.com" and len(parts) >= 2:
            out.append(f"[![GitHub stars](https://img.shields.io/github/stars/{parts[0]}/{parts[1]}?logo=github&label=stars&color=24292f)]"
                       f"({e['code']})")
        else:
            out.append(f"[![code](https://img.shields.io/badge/code-{shield_text(parsed.netloc)}-24292f)]({e['code']})")
    if e.get("venue"):
        out.append(f"![{e['venue']}](https://img.shields.io/badge/{shield_text(e['venue'])}-8250df)")
    return " ".join(out)


def anchor(text):
    """The link GitHub generates for a heading: lower case, punctuation and emoji dropped, spaces to hyphens."""
    return "#" + re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


def heading(key):
    icon, name, _ = SECTIONS[key]
    return f"{icon} {name}"


def link_of(e):
    return e.get("url") or f"https://arxiv.org/abs/{e['arxiv']}"


def entry_md(e):
    authors = e["authors"] if len(e["authors"]) <= 4 else e["authors"][:3] + ["et al."]
    byline = ", ".join(authors).replace(", et al.", " et al.")
    lines = [f"- **[{e['title']}]({link_of(e)})**<br>",
             f"  {badges(e)}<br>",
             f"  <sub>{byline} · {e['date']:%b %Y}</sub><br>",
             f"  {e['summary']}" + ("<br>" if e.get("result") else "")]
    if e.get("result"):
        lines.append(f"  📈 **Reported:** {e['result']}")
    return "\n".join(lines) + "\n"


def render(entries):
    latest = entries[0]["date"] if entries else "none"
    badge_row = " ".join([
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        f"![Entries](https://img.shields.io/badge/entries-{len(entries)}-2563eb)",
        f"![Latest entry](https://img.shields.io/badge/{shield_text('latest entry')}-{shield_text(str(latest))}-0f766e)",
        "[![PRs welcome](https://img.shields.io/badge/PRs-welcome-16a34a)](CONTRIBUTING.md)",
    ])
    overview = ["| | Section | What it covers | Entries |", "|:---:|:---|:---|:---:|"]
    sections = []
    for key, (icon, name, blurb) in SECTIONS.items():
        group = [e for e in entries if e["category"] == key]
        if not group:
            continue
        overview.append(f"| {icon} | [{name}]({anchor(heading(key))}) | {blurb} | {len(group)} |")
        sections.append(f"## {heading(key)}\n\n<sub>{blurb} {len(group)} entries, newest first.</sub>\n\n"
                        + "\n".join(entry_md(e) for e in group)
                        + '\n<p align="right"><sub><a href="#readme-top">⬆ back to top</a></sub></p>\n')
    recent = ["| Date | Work | Section |", "|:---:|:---|:---|"]
    for e in entries[:5]:
        title = e["title"].replace("|", "\\|")
        date = str(e["date"]).replace("-", "\u2011")  # non-breaking hyphens keep the date on one line
        recent.append(f"| {date} | [{title}]({link_of(e)}) | [{heading(e['category'])}]({anchor(heading(e['category']))}) |")
    template = (ROOT / "template.md").read_text(encoding="utf-8")
    return (template.replace("{{badges}}", badge_row)
                    .replace("{{overview}}", "\n".join(overview))
                    .replace("{{recent}}", "\n".join(recent))
                    .replace("{{sections}}", "\n".join(sections)))


def main():
    errors = []
    entries = load(errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    readme = render(entries)
    path = ROOT / "README.md"
    if "--check" in sys.argv:
        if not path.exists() or path.read_text(encoding="utf-8") != readme:
            print("README.md is out of date: run python3 build.py and commit the result", file=sys.stderr)
            sys.exit(1)
        print(f"ok: {len(entries)} entries")
        return
    path.write_text(readme, encoding="utf-8")
    print(f"wrote README.md: {len(entries)} entries")


if __name__ == "__main__":
    main()

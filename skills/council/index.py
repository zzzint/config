#!/usr/bin/env python3
"""Rebuild the council index. Usage: python3 index.py [reports-dir]

Reads <meta name="council"> from every page in reports-dir (default: reports/ beside this script) and
writes reports-dir/index.html: one table, newest reviewed first. Pages without the meta (old format)
are listed by filename under "Older pages"."""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DIRECTIONS = ("yes", "maybe", "no")
STYLE = """
  :root{--bg:#f6f4ef;--ink:#1d1b17;--muted:#6b665c;--rule:#d9d4c8;--card:#fffdf8;
        --block:#a4262c;--fix:#b3660a;--q:#2f5f8f;--verify:#5a4a7a;--ok:#2f6b3a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman",serif}
  header,main{max-width:120ch;margin:0 auto;padding:0 1.5rem}
  header{padding-top:2.5rem;padding-bottom:1rem;border-bottom:1px solid var(--rule)}
  h1{font:600 1.55rem/1.2 Georgia,serif;margin:0 0 .25rem}
  .meta{color:var(--muted);font-size:.9rem;margin:0}
  h2{font:600 .8rem/1 ui-monospace,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:2.25rem 0 .75rem}
  table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--rule)}
  th{font:.72rem ui-monospace,Menlo,monospace;color:var(--muted);text-align:left;padding:.5rem .6rem;border-bottom:1px solid var(--rule)}
  td{padding:.5rem .6rem;border-bottom:1px solid var(--rule);vertical-align:top}
  td:first-child{border-left:4px solid var(--rule);white-space:nowrap}
  tr.yes td:first-child{border-left-color:var(--ok)} tr.maybe td:first-child{border-left-color:var(--fix)} tr.no td:first-child{border-left-color:var(--block)}
  .num,.mono,code{font:.85rem ui-monospace,Menlo,monospace}
  .num{text-align:right}
  .dot{display:inline-block;width:.6rem;height:.6rem;border-radius:50%;margin-right:.35rem;background:var(--rule)}
  .yes .dot{background:var(--ok)} .maybe .dot{background:var(--fix)} .no .dot{background:var(--block)}
  a{color:var(--q);text-decoration:none;border-bottom:1px dotted var(--q)}
  ul.older{padding-left:1.1rem;font:.85rem ui-monospace,Menlo,monospace} ul.older li{margin:.2rem 0}
"""


class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.content = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name") == "council" and self.content is None:
            self.content = a.get("content") or ""


def read_meta(path):
    p = Meta()
    p.feed(path.read_text(encoding="utf-8", errors="replace"))
    if p.content is None:
        return None
    try:
        data = json.loads(p.content)
        int(data["pr"]), data["owner"], data["repo"], data["reviewed"]
        return data
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        print(f"{path.name}: unreadable council meta ({e}), listed as an older page", file=sys.stderr)
        return None


def row(path, m):
    e = lambda v: html.escape(str(v if v is not None else ""))
    d = m.get("direction") if m.get("direction") in DIRECTIONS else ""
    c = m.get("counts") or {}
    nums = "".join(f'<td class="num">{e(c.get(k, ""))}</td>' for k in ("do", "decide", "verify", "nits"))
    title = re.sub(r"`([^`]+)`", r"<code>\1</code>", e(m.get("title")))
    return (f'<tr class="{d}"><td><a href="{e(path.name)}">{e(m["owner"])}/{e(m["repo"])}#{e(m["pr"])}</a></td>'
            f'<td>{title}</td><td>{e(m.get("author"))}</td><td class="mono">{e(m.get("label") or "—")}</td><td class="mono">{e(m.get("tier"))}</td>'
            f'<td class="{d}"><span class="dot"></span>{e(d or "?")}</td>{nums}'
            f'<td class="mono">{e(str(m.get("head", ""))[:8])}</td><td class="mono">{e(m.get("reviewed"))}</td></tr>')


def build(reports):
    pages, older = [], []
    for path in sorted(reports.glob("*.html")):
        if path.name == "index.html" or path.name.endswith("-example.html"):
            continue
        m = read_meta(path)
        (pages.append((path, m)) if m else older.append(path))
    pages.sort(key=lambda pm: (str(pm[1]["reviewed"]), int(pm[1]["pr"])), reverse=True)
    rows = "\n".join(row(p, m) for p, m in pages) or '<tr><td colspan="12">No pages with council meta yet.</td></tr>'
    older_html = ""
    if older:
        items = "\n".join(f'  <li><a href="{html.escape(p.name)}">{html.escape(p.name)}</a></li>' for p in older)
        older_html = f'<h2>Older pages</h2>\n<ul class="older">\n{items}\n</ul>\n'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Council · index</title>
<style>{STYLE}</style>
</head>
<body>
<header>
  <h1>Council reviews</h1>
  <p class="meta">{len(pages)} pages, newest reviewed first.</p>
</header>
<main>
<h2>Reviews</h2>
<table>
<thead><tr><th>PR</th><th>Title</th><th>Author</th><th>Label</th><th>Tier</th><th>Direction</th><th>Do</th><th>Decide</th><th>Verify</th><th>Nits</th><th>Head</th><th>Reviewed</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
{older_html}</main>
</body>
</html>
"""


if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit(__doc__)
    reports = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(__file__).resolve().parent / "reports"
    if not reports.is_dir():
        sys.exit(f"no reports directory at {reports}")
    out = reports / "index.html"
    out.write_text(build(reports), encoding="utf-8")
    print(out)

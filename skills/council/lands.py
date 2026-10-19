#!/usr/bin/env python3
"""Fill every a.lands link on a council page from its data-cite. Usage: python3 lands.py <page.html>

The chair writes data-cite ("<path>:<line>", "<path>:<a>-<b>" or "PR") and leaves the a.lands href
and text as anything; this rewrites both from data-cite and the page's <meta name="council">.
A path anchor is GitHub's Files changed fragment: #diff-<sha256 hex of the path>R<line>."""
import hashlib
import html
import json
import re
import sys
from pathlib import Path


def href(owner: str, repo: str, pr: int, cite: str) -> str:
    base = f"https://github.com/{owner}/{repo}/pull/{pr}"
    if cite == "PR":
        return base
    m = re.fullmatch(r"(\S+):(\d+)(?:-(\d+))?", cite)
    if m is None:
        sys.exit(f"bad data-cite {cite!r}")
    span = f"R{m[2]}" + (f"-R{m[3]}" if m[3] else "")
    return f"{base}/files#diff-{hashlib.sha256(m[1].encode()).hexdigest()}{span}"


def fill(page: str) -> str:
    meta = json.loads(html.unescape(re.search(r"<meta name=\"council\" content='(.*?)'>", page)[1]))
    owner, repo, pr = meta["owner"], meta["repo"], meta["pr"]

    def item(m: re.Match) -> str:
        block = m[0]
        cite = re.search(r'data-cite="([^"]+)"', block)[1]
        text = "the PR conversation" if cite == "PR" else cite
        return re.sub(r'<a class="lands" href="[^"]*">.*?</a>',
                      f'<a class="lands" href="{href(owner, repo, pr, cite)}">{html.escape(text)}</a>', block, flags=re.S)

    page = re.sub(r'<article class="card[^>]*>.*?</article>', item, page, flags=re.S)
    return re.sub(r'<li id="n\d+"[^>]*>.*?</li>', item, page, flags=re.S)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    p = Path(sys.argv[1])
    p.write_text(fill(p.read_text(encoding="utf-8")), encoding="utf-8")

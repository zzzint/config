#!/usr/bin/env python3
"""Mechanical language floor for a council page. Usage: python3 floor.py <page.html>

Two checks — ends in a full stop, at least five words — applied to:
  * the essence and direction paragraphs;
  * every <dd>, except <dd class="where">; a Fix size <dd> needs only the full stop (terse by design);
  * every nit <li> inside <ul class="lines">, on the text before its trailing cite;
  * every <p> inside <section class="primer">, except class="where", after its label is stripped.
Exit 0 when clean, 1 with one line per failure. A mechanical floor only — sentence quality is the
editor's job (EDITOR.md); a verb check was tried and misfired on imperatives, so there is none."""
import html, pathlib, re, sys

CITE_TAIL = re.compile(r"\s*—\s*(?:\S+:\d+(?:-\d+)?\)?|see the #\d+ review's primer\.)\s*$")
LABEL = re.compile(r"^(what it is|where it lives|why it mattered here|read next|already taught)\s*", re.I)


def text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def three(t: str) -> list[str]:
    return [
        w
        for w, bad in (
            ("no full stop", not t.endswith(".")),
            ("under five words", len(t.split()) < 5),
        )
        if bad
    ]


def check(page: str) -> list[str]:
    fails: list[str] = []
    for m in re.finditer(r"<dt>(?P<label>[^<]*)</dt><dd(?P<attrs>[^>]*)>(?P<body>.*?)</dd>", page, re.S):
        if 'class="where"' in m["attrs"]:
            continue
        t = text(m["body"])
        if m["label"].strip() == "Fix size":  # terse by design: a full stop, nothing else
            if not t.endswith("."):
                fails.append(f"dd [Fix size: no full stop]: {t[:100]}")
            continue
        if why := three(t):
            fails.append(f"dd [{', '.join(why)}]: {t[:100]}")
    for ul in re.finditer(r'<ul class="lines">(.*?)</ul>', page, re.S):
        for li in re.findall(r"<li>(.*?)</li>", ul[1], re.S):
            t = LABEL.sub("", CITE_TAIL.sub("", text(li)))
            if not t.endswith("."):
                fails.append(f"li [no full stop before cite]: {t[:100]}")
    for m in re.finditer(r'<p class="(?P<cls>essence|verdict)">(?P<body>.*?)</p>', page, re.S):
        t = text(m["body"])
        if why := three(t):
            fails.append(f"{m['cls']} [{', '.join(why)}]: {t[:100]}")
    for sec in re.finditer(r'<section class="primer">(.*?)</section>', page, re.S):
        for p in re.finditer(r"<p(?P<attrs>[^>]*)>(?P<body>.*?)</p>", sec[1], re.S):
            if 'class="where"' in p["attrs"]:
                continue
            t = LABEL.sub("", text(p["body"]))
            if why := three(t):
                fails.append(f"primer [{', '.join(why)}]: {t[:100]}")
    return fails


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    failures = check(pathlib.Path(sys.argv[1]).read_text())
    for f in failures:
        print(f)
    print(f"{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)

#!/usr/bin/env python3
"""Language floor for a council page. Usage: python3 floor.py <page.html> [--diff PR<N>.diff]

Enforces the caps in FORMAT.md on the selectors in REPORT.html:
  * words per sentence: prose <= 25, drafts <= 35 (a <code> or `backtick` span is one word);
  * sentences per field, no ';' and no spaced em dash (prose only, drafts exempt), ends with '.' (a draft may end '?'), >= 5 words
    (Fix size is exempt from the word minimum);
  * every card has non-empty ask and direct drafts, and the ask draft contains '?';
  * a draft holds at most 3 code spans, and no two-word opener starts more than a quarter of the page's drafts
    (cards, follow-ups and nits together);
  * no link to another local .html page, except a carried-forward card's "from #M" tag; none in the primer;
  * primer optional, at most 3 concepts, only p.idea / p.here / p.read;
  * section#scope first in <main>: class and <b> agree (needed, trim, questionable), why in 1-2 sentences,
    needed has no cuts, trim has 1 to 5, each cut has span.lines "−N", each cut and unasked item is one sentence
    with a head-SHA blob link and no a.lands, draft or checkbox, and an h3 comes before each list;
  * follow-ups (h2#followups + ul.followups li#u<N>, after the cards, before the nits) follow the nit rules,
    without the "nit:" prefix;
  * <meta name="council"> present, valid JSON, every key valid, counts matching the page, scope matching the panel,
    lean matching span.lean, at least the sum of the cuts, and 0 when the scope is needed;
  * every card, follow-up and nit has an a.lands link to its data-cite in the PR's Files changed view
    (#diff-<sha256 of path>R<line>), or to the PR itself when data-cite is "PR";
  * with --diff: every data-cite line sits inside a hunk of the PR diff, so GitHub can attach the comment there.
Exit 0 when clean, 1 with one line per failure and a count. Sentence quality is the editor's job (EDITOR.md)."""
import datetime
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

CODE = "\u24b8"  # one-token stand-in for a code span
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ABBREV = re.compile(r"\b(e\.g|i\.e|etc|vs|cf|approx|a\.k\.a|Mr|Mrs|Ms|Dr)\.(?=\s)", re.I)
SENTENCE_END = re.compile(r"(?<=[.?!])[\"'\u201d\u2019)\]]*\s+")
CLOSERS = "\"'\u201d\u2019)]"
FOOTER = "Nothing was executed; every cite on this page was read in the source at the reviewed commit."
EVIDENCE = ["Context", "Where", "Finding", "Recommendation", "Fix size", "Judgement call", "Reply"]
EVIDENCE_SENTENCES = {"Context": (1, 1), "Finding": (1, 4), "Recommendation": (1, 3), "Judgement call": (1, 2), "Reply": (1, 2)}
GROUPS = ("do", "decide", "verify")
SCOPES = {"needed": "Needed.", "trim": "Trim.", "questionable": "Questionable."}
CITE = re.compile(r"(?P<path>\S+):(?P<a>\d+)(?:-(?P<b>\d+))?|PR")


def diff_lines(diff: str) -> dict[str, set[int]]:
    """Right-side (head) line numbers inside each file's hunks: added and context lines."""
    lines: dict[str, set[int]] = {}
    path, n = None, 0
    for row in diff.splitlines():
        if row.startswith("+++ "):
            target = row[4:].strip()
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            if path:
                lines.setdefault(path, set())
        elif row.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", row)
            n = int(m[1]) if m else 0
        elif path is None or row.startswith(("--- ", "diff ", "index ")):
            continue
        elif row.startswith(("+", " ")):
            lines[path].add(n)
            n += 1
        elif row == "":
            lines[path].add(n)  # a blank context line some tools strip to ""
            n += 1
    return lines


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.kids = tag, {k: v or "" for k, v in attrs}, parent, []

    @property
    def cls(self):
        return self.attrs.get("class", "").split()

    def walk(self):
        for k in self.kids:
            if isinstance(k, Node):
                yield k
                yield from k.walk()

    def all(self, tag=None, cls=None, **attrs):
        return [n for n in self.walk() if (tag is None or n.tag == tag) and (cls is None or cls in n.cls)
                and all(n.attrs.get(k) == v for k, v in attrs.items())]

    def one(self, tag=None, cls=None, **attrs):
        found = self.all(tag, cls, **attrs)
        return found[0] if found else None

    def within(self, pred):
        n = self.parent
        while n is not None:
            if pred(n):
                return n
            n = n.parent
        return None

    def raw(self):
        return "".join(k if isinstance(k, str) else k.raw() for k in self.kids)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("#root", [], None)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.kids.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.kids.append(data)


def text(node, drop=lambda n: False):
    """Visible text with each <code> span collapsed to one token; `drop` removes label nodes."""
    out = []
    for k in node.kids:
        if isinstance(k, str):
            out.append(k)
        elif k.tag == "code":
            out.append(CODE)
        elif k.tag == "br":
            out.append(" ")
        elif not drop(k):
            out.append(text(k, drop))
    return "".join(out)


def clean(t):
    t = re.sub(r"`[^`\n]+`", CODE, t)
    return re.sub(r"\s+", " ", t).strip()


def words(t):
    return len([w for w in t.split() if re.search(rf"[\w{CODE}]", w)])


def sentences(t):
    return [s for s in SENTENCE_END.split(ABBREV.sub(lambda m: m[1].replace(".", ""), t)) if s.strip()]


def show(t):
    t = t.replace(CODE, "`code`")
    return t if len(t) <= 90 else t[:87] + "..."


def lis(ul):
    return [k for k in ul.kids if isinstance(k, Node) and k.tag == "li"] if ul is not None else []


class Floor:
    def __init__(self, diff=None):
        self.fails = []
        self.diff = diff
        self.target = None  # (owner, repo, pr) from the meta, for a.lands
        self.head = None  # full head SHA from the meta, for the scope panel's blob links
        # A page written before the Scope panel existed: no meta "scope" key and no section#scope.
        # It is held to the rules of its time, so editing its drafts and re-running floor still works.
        self.pre_scope = False

    def lands(self, where, node, cite):
        if not CITE.fullmatch(cite):
            return self.fail(where, 'data-cite must be "<path>:<line>", "<path>:<a>-<b>" or "PR"')
        links = node.all("a", "lands") if node is not None else []
        if len(links) != 1:
            return self.fail(where, f"needs exactly one a.lands link to where the comment goes, found {len(links)}")
        if self.target is None:
            return
        owner, repo, pr = self.target
        base = f"https://github.com/{owner}/{repo}/pull/{pr}"
        m = CITE.fullmatch(cite)
        if cite == "PR":
            want = base
        else:
            span = f"R{m['a']}" + (f"-R{m['b']}" if m["b"] else "")
            want = f"{base}/files#diff-{hashlib.sha256(m['path'].encode()).hexdigest()}{span}"
        if links[0].attrs.get("href") != want:
            self.fail(where, f"a.lands should be {want}, found {links[0].attrs.get('href')!r}")
        if self.diff is None or cite == "PR":
            return
        hunk = self.diff.get(m["path"])
        if hunk is None:
            return self.fail(where, f"{m['path']} is not in the PR diff, so GitHub cannot attach a comment there; anchor on a diff line or use \"PR\"")
        for line in {int(m["a"]), int(m["b"] or m["a"])}:
            if line not in hunk:
                self.fail(where, f"{m['path']}:{line} is outside the diff hunks; anchor on a line GitHub shows in Files changed, or use \"PR\"")

    def fail(self, where, msg):
        self.fails.append(f"{where}: {msg}")

    def field(self, where, raw, *, count=(1, 99), cap=25, ends=".", min_words=5, ask=False, prose=True):
        t = clean(raw)
        if not t:
            return self.fail(where, "empty")
        if prose and ";" in t:
            self.fail(where, f"contains ';': {show(t)}")
        if prose and re.search(r"\s\u2014\s", t):
            self.fail(where, f"contains a spaced em dash: {show(t)}")
        if not prose and t.count(CODE) > 3:
            self.fail(where, f"{t.count(CODE)} code spans (at most 3 in a draft; lead with what the author will recognise): {show(t)}")
        if not t.rstrip(CLOSERS).endswith(tuple(ends)):
            self.fail(where, f"must end with {' or '.join(repr(e) for e in ends)}: {show(t[-60:])}")
        if min_words and words(t) < min_words:
            self.fail(where, f"under {min_words} words: {show(t)}")
        if ask and "?" not in t:
            self.fail(where, f"ask draft has no '?': {show(t)}")
        parts = sentences(t)
        lo, hi = count
        if not lo <= len(parts) <= hi:
            want = f"exactly {lo}" if lo == hi else f"at most {hi}"
            self.fail(where, f"{len(parts)} sentences ({want}): {show(t)}")
        for i, s in enumerate(parts, 1):
            if (n := words(s)) > cap:
                self.fail(where, f"sentence {i} has {n} words (cap {cap}): {show(s)}")

    def meta_scope(self, data, page):
        """The meta's scope and lean against the Scope panel."""
        scope, lean = data.get("scope"), data.get("lean")
        if not isinstance(scope, str) or scope not in SCOPES:
            self.fail("meta", f"'scope' must be {', '.join(SCOPES)}")
        elif page["scope"] and scope != page["scope"]:
            self.fail("meta", f"scope is {scope!r} but section#scope says {page['scope']!r}")
        if not isinstance(lean, int) or isinstance(lean, bool) or lean < 0:
            return self.fail("meta", "'lean' missing or not an integer >= 0")
        if lean < page["cut"]:
            self.fail("meta", f"lean is {lean} but the cuts add up to {page['cut']} lines")
        if scope == "needed" and lean:
            self.fail("meta", f"lean is {lean} but must be 0 when scope is needed")
        if page["lean"] is not None and lean != page["lean"]:
            self.fail("meta", f"lean is {lean} but span.lean says {page['lean']}")

    def meta(self, root, page):
        m = root.one("meta", name="council")
        if m is None:
            return self.fail("meta", 'missing <meta name="council">')
        try:
            data = json.loads(m.attrs.get("content", ""))
        except json.JSONDecodeError as e:
            return self.fail("meta", f"content is not valid JSON ({e})")
        if not isinstance(data, dict):
            return self.fail("meta", "content is not a JSON object")
        str_keys = ("owner", "repo", "title", "author", "head", "reviewed", "tier", "direction")
        for k in str_keys:
            if not isinstance(data.get(k), str) or not data[k].strip():
                self.fail("meta", f"'{k}' missing or not a non-empty string")
        if not isinstance(data.get("pr"), int) or isinstance(data.get("pr"), bool):
            self.fail("meta", "'pr' missing or not an integer")
        if isinstance(data.get("head"), str) and not re.fullmatch(r"[0-9a-f]{40}", data["head"]):
            self.fail("meta", "'head' is not a full 40-character SHA")
        if isinstance(data.get("reviewed"), str):
            try:
                datetime.date.fromisoformat(data["reviewed"])
            except ValueError:
                self.fail("meta", "'reviewed' is not YYYY-MM-DD")
        for k, allowed in (("tier", ("light", "full")), ("direction", ("yes", "maybe", "no"))):
            if isinstance(data.get(k), str) and data[k] not in allowed:
                self.fail("meta", f"'{k}' must be {' or '.join(allowed)}")
        if self.pre_scope:
            if isinstance(data.get("counts"), dict):
                data["counts"].setdefault("followups", 0)
        else:
            self.meta_scope(data, page)
        keys = (*GROUPS, "followups", "nits")
        counts = data.get("counts")
        if not isinstance(counts, dict) or any(not isinstance(counts.get(k), int) for k in keys):
            return self.fail("meta", f"'counts' must hold integer {', '.join(keys)}")
        for k in keys:
            if counts[k] != page[k]:
                self.fail("meta", f"counts.{k} is {counts[k]} but the page has {page[k]}")
        if page["direction"] and data.get("direction") != page["direction"]:
            self.fail("meta", f"direction is {data.get('direction')!r} but p.verdict says {page['direction']!r}")

    def header(self, root):
        h = root.one("header")
        if h is None:
            return self.fail("header", "missing <header>"), None
        for tag, cls in (("h1", None), ("p", "meta"), ("p", "essence"), ("p", "verdict"), ("p", "counts")):
            if h.one(tag, cls) is None:
                self.fail("header", f"missing {tag}{'.' + cls if cls else ''}")
        label = lambda n: "q" in n.cls
        if (e := h.one("p", "essence")) is not None:
            self.field("p.essence", text(e, label), count=(1, 4))
        v = h.one("p", "verdict")
        if v is None:
            return None
        direction = next((c for c in v.cls if c in ("yes", "maybe", "no")), None)
        if direction is None:
            self.fail("p.verdict", "class needs yes, maybe or no")
        b = v.one("b")
        answer = clean(text(b)) if b else ""
        if answer not in ("Yes.", "Maybe.", "No."):
            self.fail("p.verdict", f"needs <b>Yes.</b>, <b>Maybe.</b> or <b>No.</b>, found {answer!r}")
        elif direction and answer.lower() != direction + ".":
            self.fail("p.verdict", f"class {direction!r} disagrees with <b>{answer}</b>")
        self.field("p.verdict", text(v, lambda n: label(n) or n is b), count=(1, 3))
        return direction

    def primer(self, root):
        d = root.one("details", id="primer")
        slugs = set()
        if d is None:
            return slugs
        concepts = d.all("section", "primer")
        if len(concepts) > 3:
            self.fail("primer", f"{len(concepts)} concepts (at most 3)")
        s = d.one("summary")
        m = re.fullmatch(r"Primer \u2014 (\d+) concepts? this page assumes", clean(text(s)) if s else "")
        if not m:
            self.fail("primer", 'summary must read "Primer \u2014 N concepts this page assumes"')
        elif int(m[1]) != len(concepts):
            self.fail("primer", f"summary says {m[1]} concepts but there are {len(concepts)}")
        for k in d.kids:
            if isinstance(k, Node) and k.tag != "summary" and not (k.tag == "section" and "primer" in k.cls):
                self.fail("primer", f"only a summary and section.primer belong in the primer, found <{k.tag}>")
        label = lambda n: "k" in n.cls
        for sec in concepts:
            sid = sec.attrs.get("id", "")
            where = f"primer #{sid or '?'}"
            if not re.fullmatch(r"p-[a-z0-9-]+", sid):
                self.fail(where, 'section needs id="p-<slug>"')
            slugs.add(sid)
            if sec.one("h3") is None:
                self.fail(where, "missing h3")
            for k in sec.kids:
                if isinstance(k, Node) and k.tag != "h3" and not (k.tag == "p" and set(k.cls) & {"idea", "here", "read"}):
                    self.fail(where, f"only h3, p.idea, p.here, p.read belong here, found <{k.tag} class={' '.join(k.cls)!r}>")
            idea, here, read = sec.one("p", "idea"), sec.one("p", "here"), sec.one("p", "read")
            if idea is None or here is None:
                self.fail(where, "needs p.idea and p.here")
            if idea is not None:
                self.field(f"{where} p.idea", text(idea, label), count=(1, 1))
            if here is not None:
                self.field(f"{where} p.here", text(here, label), count=(1, 2))
            if read is not None and len(read.all("a")) != 1:
                self.fail(f"{where} p.read", "needs exactly one link")
        return slugs

    def scope(self, root):
        """section#scope, first in <main>. Returns what meta() compares: the verdict, span.lean, the sum of the cuts."""
        out = {"scope": None, "lean": None, "cut": 0}
        sec = root.one("section", id="scope")
        if sec is None:
            if not self.pre_scope:
                self.fail("scope", "missing section#scope (required on every page written since the panel was added)")
            return out
        main = root.one("main")
        if main is None or next((k for k in main.kids if isinstance(k, Node)), None) is not sec:
            self.fail("scope", "section#scope must be the first child of <main>, before the primer")
        verdict = [c for c in sec.cls if c in SCOPES]
        if "scope" not in sec.cls or len(verdict) != 1:
            self.fail("scope", f'class must be "scope" plus one of {", ".join(SCOPES)}')
        else:
            out["scope"] = verdict[0]
        p = sec.one("p", "scope-verdict")
        if p is None:
            self.fail("scope", "missing p.scope-verdict")
        else:
            b = p.one("b")
            answer = clean(text(b)) if b else ""
            if answer not in SCOPES.values():
                self.fail("p.scope-verdict", f"needs <b>{'</b>, <b>'.join(SCOPES.values())}</b>, found {answer!r}")
            elif out["scope"] and answer != SCOPES[out["scope"]]:
                self.fail("p.scope-verdict", f"class {out['scope']!r} disagrees with <b>{answer}</b>")
            self.field("p.scope-verdict", text(p, lambda n: "q" in n.cls or n is b), count=(1, 2))
        kids, lists = [k for k in sec.kids if isinstance(k, Node)], {}
        for i, k in enumerate(kids):
            name = next((c for c in k.cls if c in ("cuts", "unasked")), None) if k.tag == "ul" else None
            if name:
                lists[name] = k
                if i == 0 or kids[i - 1].tag != "h3":
                    self.fail("scope", f"ul.{name} needs its h3 just before it")
                if not lis(k):
                    self.fail("scope", f"ul.{name} is empty; omit it and its h3")
            elif k.tag == "h3":
                if i + 1 == len(kids) or kids[i + 1].tag != "ul":
                    self.fail("scope", "an h3 without its list; omit both when the list is empty")
            elif not (k.tag == "p" and "scope-verdict" in k.cls):
                self.fail("scope", f"only p.scope-verdict, h3, ul.cuts and ul.unasked belong here, found <{k.tag}>")
        cuts = lis(lists.get("cuts"))
        if out["scope"] == "needed" and cuts:
            self.fail("scope", "needed has no cuts; a page with cuts is trim")
        if out["scope"] == "trim" and not cuts:
            self.fail("scope", "trim needs at least one cut")
        if len(cuts) > 5:
            self.fail("scope", f"{len(cuts)} cuts (at most 5)")
        for i, li in enumerate(cuts, 1):
            self.scope_item(f"scope cut {i}", li)
            span = li.one("span", "lines")
            m = re.fullmatch(r"[\u2212-](\d+)", clean(text(span)) if span else "")
            if not m or int(m[1]) < 1:
                self.fail(f"scope cut {i}", 'needs span.lines "\u2212N" with N >= 1')
            else:
                out["cut"] += int(m[1])
        for i, li in enumerate(lis(lists.get("unasked")), 1):
            self.scope_item(f"scope unasked {i}", li)
        if cuts:
            lean = sec.one("span", "lean")
            m = re.fullmatch(r"about (\d+) lines?", clean(text(lean)) if lean else "")
            if m:
                out["lean"] = int(m[1])
            else:
                self.fail("scope", 'the "Could cut" h3 needs span.lean "about N lines"')
        return out

    def scope_item(self, where, li):
        """A cut or an unasked item: one sentence and a head-SHA blob link to its data-cite. Not a comment."""
        cite = li.attrs.get("data-cite", "")
        m = CITE.fullmatch(cite)
        if m is None or cite == "PR":
            self.fail(where, 'data-cite must be "<path>:<line>" or "<path>:<a>-<b>"')
        if li.all("a", "lands") or li.all("div", "draft") or li.all("input"):
            self.fail(where, "scope items are not comments: no a.lands, draft or checkbox")
        t = li.one("span", "text")
        if t is None:
            self.fail(where, "missing span.text")
        else:
            self.field(f"{where} span.text", text(t), count=(1, 1))
        w = li.one("span", "where")
        links = w.all("a") if w else []
        if len(links) != 1:
            return self.fail(where, "needs span.where with one link")
        if self.target and self.head and m and cite != "PR":
            owner, repo, _ = self.target
            want = f"https://github.com/{owner}/{repo}/blob/{self.head}/{m['path']}#L{m['a']}" + (f"-L{m['b']}" if m["b"] else "")
            if links[0].attrs.get("href") != want:
                self.fail(where, f"link should be the head-SHA blob link {want}, found {links[0].attrs.get('href')!r}")

    def card(self, art, slugs):
        cid = art.attrs.get("id", "")
        where = f"#{cid or '?'}"
        m = re.fullmatch(r"f(\d+)", cid)
        if not m:
            self.fail(where, 'card needs id="f<N>"')
        group = [c for c in art.cls if c in GROUPS]
        if len(group) != 1:
            self.fail(where, "card class needs exactly one of do, decide, verify")
        self.lands(where, art.one("fieldset", "pick"), art.attrs.get("data-cite", ""))
        h3 = art.one("h3")
        n = h3.one("span", "n") if h3 else None
        if n is None or (m and clean(text(n)) != f"#{m[1]}"):
            self.fail(where, f'h3 needs span.n "#{m[1] if m else "N"}"')
        why = art.one("p", "why")
        if why is None:
            self.fail(where, "missing p.why")
        else:
            self.field(f"{where} p.why", text(why), count=(1, 1))
        tags = art.one("div", "tags")
        if tags is None or not tags.all("span", "tag"):
            self.fail(where, "needs div.tags with at least one span.tag")
        for a in tags.all("a", "assumes") if tags else []:
            if a.attrs.get("href", "") not in {f"#{s}" for s in slugs}:
                self.fail(where, f"a.assumes points at {a.attrs.get('href')!r}, not a primer concept on this page")
        pick = art.one("fieldset", "pick")
        if pick is None:
            return self.fail(where, "missing fieldset.pick")
        radios = [r for r in pick.all("input") if r.attrs.get("type") == "radio"]
        if sorted(r.attrs.get("value") for r in radios) != ["ask", "direct", "skip"] \
                or any(r.attrs.get("name") != f"pick-{cid}" for r in radios):
            self.fail(where, f'needs radios ask, direct, skip named "pick-{cid}"')
        checked = [r.attrs.get("value") for r in radios if "checked" in r.attrs]
        want = "skip" if group == ["verify"] else "ask"
        if checked != [want]:
            self.fail(where, f"default pick must be {want!r}, found {checked}")
        if any(r.within(lambda p: p.tag == "label") is None for r in radios):
            self.fail(where, "every radio needs a label")
        for framing in ("ask", "direct"):
            d = pick.one("div", "draft", **{"data-framing": framing})
            if d is None:
                self.fail(where, f'missing div.draft[data-framing="{framing}"]')
                continue
            if d.attrs.get("contenteditable") != "true":
                self.fail(where, f'{framing} draft needs contenteditable="true"')
            ends = (".", "?")
            self.field(f"{where} draft[{framing}]", text(d), count=(1, 2), cap=35, ends=ends, ask=framing == "ask", prose=False)
        ev = art.one("details", "evidence")
        summary = ev.one("summary") if ev else None
        if ev is None or summary is None or clean(text(summary)) != "Evidence":
            return self.fail(where, 'needs details.evidence with summary "Evidence"')
        rows, label = [], None
        for k in (ev.one("dl") or ev).kids:
            if isinstance(k, Node) and k.tag == "dt":
                label = clean(text(k))
            elif isinstance(k, Node) and k.tag == "dd":
                rows.append((label, k))
        labels = [r[0] for r in rows]
        expected = [x for x in EVIDENCE if x in labels]
        if any(x not in EVIDENCE for x in labels) or labels != expected:
            self.fail(where, f"evidence labels must be, in order, {', '.join(EVIDENCE)}; found {labels}")
        for x in EVIDENCE:
            if x != "Judgement call" and x not in labels:
                self.fail(where, f"evidence missing {x}")
        for label, dd in rows:
            if label == "Where":
                if "where" not in dd.cls or not dd.all("a"):
                    self.fail(f"{where} Where", "needs dd.where with at least one link")
            elif label == "Fix size":
                self.field(f"{where} Fix size", text(dd), min_words=0)
            elif label in EVIDENCE_SENTENCES:
                self.field(f"{where} {label}", text(dd), count=EVIDENCE_SENTENCES[label])

    def variety(self, root):
        """No two-word opener starts more than a quarter of the page's drafts (at least 2 allowed)."""
        openers = []
        for d in root.all("div", "draft"):
            body = re.sub(r"^nit:\s*", "", clean(text(d)), flags=re.I)
            words_ = re.findall(r"[\w'\u2019]+", body.lower())[:2]
            if len(words_) == 2:
                openers.append(" ".join(words_))
        limit = max(2, -(-len(openers) // 4))
        for opener in sorted(set(openers)):
            if (n := openers.count(opener)) > limit:
                self.fail("drafts", f'{n} of {len(openers)} drafts open with "{opener}" (at most {limit}); vary the shapes')

    def item(self, li, prefix):
        """A nit (n<N>) or a follow-up (u<N>): one unchecked checkbox, a tag, one sentence, a.lands and one draft."""
        kind = "nit" if prefix == "n" else "follow-up"
        iid = li.attrs.get("id", "")
        where = f"#{iid or '?'}"
        m = re.fullmatch(rf"{prefix}(\d+)", iid)
        if not m:
            self.fail(where, f'{kind} needs id="{prefix}<N>"')
        self.lands(where, li, li.attrs.get("data-cite", ""))
        boxes = [i for i in li.all("input") if i.attrs.get("type") == "checkbox"]
        if len(boxes) != 1 or "checked" in boxes[0].attrs:
            self.fail(where, "needs one unchecked checkbox")
        elif prefix == "u" and m and boxes[0].attrs.get("aria-label") != f"pick follow-up {m[1]}":
            self.fail(where, f'checkbox needs aria-label="pick follow-up {m[1]}"')
        if li.one("span", "tag") is None:
            self.fail(where, "missing span.tag")
        cite = li.one("span", "where")
        if cite is None or not cite.all("a"):
            self.fail(where, "needs span.where with a link")
        t = li.one("span", "text")
        if t is None:
            self.fail(where, "missing span.text")
        else:
            self.field(f"{where} span.text", text(t), count=(1, 1))
        d = li.one("div", "draft")
        if d is None:
            return self.fail(where, "missing div.draft")
        if d.attrs.get("contenteditable") != "true":
            self.fail(where, 'draft needs contenteditable="true"')
        body = clean(text(d))
        if prefix == "n" and not body.startswith("nit:"):
            self.fail(f"{where} draft", f"must start with 'nit:': {show(body)}")
        if prefix == "u" and body.lower().startswith("nit:"):
            self.fail(f"{where} draft", f"a follow-up is a ticket suggestion, not a nit; drop 'nit:': {show(body)}")
        self.field(f"{where} draft", body, count=(1, 2), cap=35, ends=(".", "?"), prose=False)

    def followups(self, root, cards):
        """h2#followups then a non-empty ul.followups, after the last card and before h2#nits; or neither."""
        h2, ul = root.one("h2", id="followups"), root.one("ul", "followups")
        if h2 is None and ul is None:
            return []
        if h2 is None or not lis(ul):
            self.fail("follow-ups", "needs both h2#followups and a non-empty ul.followups, or neither")
            return lis(ul)
        pos = {id(n): i for i, n in enumerate(root.walk())}
        nits = root.one("h2", id="nits")
        if not pos[id(h2)] < pos[id(ul)] or any(pos[id(c)] > pos[id(h2)] for c in cards) \
                or (nits is not None and pos[id(nits)] < pos[id(ul)]):
            self.fail("follow-ups", "h2#followups and ul.followups go after the last card and before h2#nits")
        return lis(ul)

    def links(self, root):
        for a in root.all("a"):
            href = a.attrs.get("href", "")
            path = href.split("#")[0].split("?")[0]
            if not path.lower().endswith((".html", ".htm")):
                continue
            if re.match(r"[a-z][a-z0-9+.-]*:", href, re.I) and not href.lower().startswith("file:"):
                continue  # absolute docs and source links are fine
            primer = a.within(lambda n: n.attrs.get("id") == "primer")
            tag = a.within(lambda n: n.tag == "span" and "tag" in n.cls)
            card = a.within(lambda n: n.tag == "article" and "card" in n.cls)
            carried = tag is not None and card is not None and clean(text(tag)).startswith("from #")
            if primer is not None or not carried:
                self.fail("link", f"{href!r} points at another page (only a card's \"from #M\" tag may)")

    def run(self, page):
        tree = Tree()
        tree.feed(page)
        tree.close()
        root = tree.root
        m = root.one("meta", name="council")
        try:
            data = json.loads(m.attrs.get("content", "")) if m is not None else {}
            self.target = (data["owner"], data["repo"], int(data["pr"]))
        except (ValueError, KeyError, TypeError):
            self.target = None  # meta() reports the problem
        else:
            self.pre_scope = "scope" not in data and root.one("section", id="scope") is None
            head = data.get("head")
            self.head = head if isinstance(head, str) and re.fullmatch(r"[0-9a-f]{40}", head) else None
        direction = self.header(root)
        scope = self.scope(root)
        slugs = self.primer(root)
        cards = root.all("article", "card")
        for art in cards:
            self.card(art, slugs)
        heads = {c for h in root.all("h2") for c in h.cls if c in GROUPS}
        for g in GROUPS:
            if any(g in c.cls for c in cards) and g not in heads:
                self.fail("groups", f"cards in {g!r} but no h2.{g}")
        followups = self.followups(root, cards)
        for li in followups:
            self.item(li, "u")
        nits = lis(root.one("ul", "nits"))
        for li in nits:
            self.item(li, "n")
        self.variety(root)
        self.links(root)
        tray = root.one("div", id="tray")
        if tray is None or tray.one("button", id="copy") is None:
            self.fail("tray", "needs div#tray with button#copy")
        scripts = root.all("script")
        if len(scripts) != 1 or "src" in scripts[0].attrs:
            self.fail("script", f"needs exactly one inline <script>, found {len(scripts)}")
        elif followups and "ul.followups li" not in scripts[0].raw():
            self.fail("script", "the tray script does not pick up ul.followups li; copy the script from REPORT.html")
        foot = root.one("footer")
        if foot is None or clean(text(foot)) != FOOTER:
            self.fail("footer", f'must read "{FOOTER}"')
        page_counts = {g: sum(g in c.cls for c in cards) for g in GROUPS}
        self.meta(root, {**page_counts, "followups": len(followups), "nits": len(nits), "direction": direction, **scope})
        return self.fails


if __name__ == "__main__":
    args = sys.argv[1:]
    diff = None
    if len(args) == 3 and args[1] == "--diff":
        diff = diff_lines(Path(args[2]).read_text(encoding="utf-8"))
        args = args[:1]
    if len(args) != 1:
        sys.exit(__doc__)
    failures = Floor(diff).run(Path(args[0]).read_text(encoding="utf-8"))
    for f in failures:
        print(f)
    print(f"{len(failures)} failure(s)")
    sys.exit(1 if failures else 0)

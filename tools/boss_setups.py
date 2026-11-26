#!/usr/bin/env python3
"""Boss gear setups from the OSRS Wiki's Recommended equipment tables, for the Boss tab.

Every page that uses {{Recommended equipment}} (Vorkath/Strategies, Zulrah/Strategies...) is fetched and each
table is read as a style (melee, ranged or magic) with ranked items per slot:

    {{Recommended equipment
    |style = Ranged (crossbow)
    |head1 = {{plink|Masori mask (f)}} / {{plink|Void ranger helm}}{{efn|Only use with the full set of Void...}}
    |head2 = {{plink|Masori mask}} / {{plink|Serpentine helm}}
    ...

The number is the rank; items in one cell are equal options in the wiki's order. A footnote ({{efn}}, possibly
a named one defined elsewhere on the page) that says an item only works as part of a full set drops it, since
the plugin picks slot by slot. Slayer helmets and black masks are dropped too: off task they do nothing, and on
a boss task the plugin's own slayer-helmet logic puts them in.

Data (c) OSRS Wiki contributors, CC BY-NC-SA 3.0. Stdlib only.
"""
import re

import wiki_recipes

TEMPLATE = "Template:Recommended equipment"
# bump when the shape of the boss data in tabs.json changes, so the Build workflow regenerates it
BOSS_DATA_VERSION = 2

# wiki parameter -> RuneLite EquipmentInventorySlot name
SLOTS = {"head": "HEAD", "neck": "AMULET", "cape": "CAPE", "body": "BODY", "legs": "LEGS", "weapon": "WEAPON",
         "shield": "SHIELD", "ammo": "AMMO", "hands": "GLOVES", "feet": "BOOTS", "ring": "RING", "special": "SPECIAL"}
PARAM = re.compile(r"^(%s)(\d+)$" % "|".join(SLOTS))

# a footnote that ties an item to a full set: the plugin picks per slot, so it can't honour that
SET_ONLY_NOTE = re.compile(r"(?i)full set|with (?:the )?full\b|full \[\[|whole set|complete set")
# only useful on a slayer task: the plugin adds these itself when the Boss tab follows a boss task
TASK_ONLY = re.compile(r"(?i)slayer helmet|black mask")


def styles_of(label):
    """The plugin style a table is for ("Ranged (crossbow)" -> ranged), or None (a hybrid or tank table)."""
    low = (label or "").lower()
    found = []
    if re.search(r"melee|stab|slash|crush", low):
        found.append("melee")
    if re.search(r"rang", low):
        found.append("ranged")
    if re.search(r"mag(?:e|ic)", low):
        found.append("magic")
    return found[0] if len(found) == 1 else None


def templates(text, name="Recommended equipment"):
    """Every top-level {{name ...}} call in the text, whole, braces balanced."""
    out = []
    for m in re.finditer(r"\{\{\s*" + re.escape(name) + r"\s*[|\n}]", text, re.I):
        end = _close(text, m.start())
        if end is not None:
            out.append(text[m.start():end])
    return out


def _close(text, start):
    """The index just past the }} matching the {{ at start, or None."""
    depth, i = 0, start
    while i < len(text) - 1:
        two = text[i:i + 2]
        if two == "{{":
            depth += 1
            i += 2
        elif two == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return i
        else:
            i += 1
    return None


def split_params(call):
    """A template call's named parameters, split on top-level pipes only."""
    body = call[2:-2]
    parts, depth, link, cur, i = [], 0, 0, [], 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "}}", "[[", "]]"):
            depth += 1 if two == "{{" else -1 if two == "}}" else 0
            link += 1 if two == "[[" else -1 if two == "]]" else 0
            cur.append(two)
            i += 2
            continue
        if body[i] == "|" and depth == 0 and link == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(body[i])
        i += 1
    parts.append("".join(cur))
    params = {}
    for p in parts[1:]:
        key, eq, value = p.partition("=")
        if eq:
            params[key.strip().lower()] = value.strip()
    return params


def named_notes(text):
    """Footnote text by name: {{efn|text|name=x}} defines x, later {{efn|name=x}} reuse it."""
    notes = {}
    for call in templates(text, "efn"):
        args = _args(call)
        name = next((a.partition("=")[2].strip() for a in args if a.strip().lower().startswith("name=")), None)
        body = next((a for a in args if not re.match(r"\s*\w+\s*=", a)), "")
        if name and body.strip():
            notes[name] = body
    return notes


def _args(call):
    body = call[2:-2]
    parts, depth, link, cur, i = [], 0, 0, [], 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "}}", "[[", "]]"):
            depth += 1 if two == "{{" else -1 if two == "}}" else 0
            link += 1 if two == "[[" else -1 if two == "]]" else 0
            cur.append(two)
            i += 2
            continue
        if body[i] == "|" and depth == 0 and link == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(body[i])
        i += 1
    parts.append("".join(cur))
    return parts[1:]


def cell_items(value, notes):
    """The items in one cell, in order, as (page, fallback page or None), set-only and task-only ones left out.
    Each item is a {{plink}} (or plinkt/plinkp) or a [[link]]; footnotes right after an item belong to it."""
    tokens = []  # ("item", page, pic) or ("note", text)
    i = 0
    while i < len(value):
        if value.startswith("{{", i):
            end = _close(value, i) or len(value)
            call = value[i:end]
            name = call[2:].split("|", 1)[0].strip().lower()
            args = _args(call)
            if name.startswith("plink") and args:
                pic = next((a.partition("=")[2].strip() for a in args[1:] if a.strip().lower().startswith("pic=")), None)
                tokens.append(("item", args[0].strip(), pic))
            elif name == "efn":
                ref = next((a.partition("=")[2].strip() for a in args if a.strip().lower().startswith("name=")), None)
                body = next((a for a in args if not re.match(r"\s*\w+\s*=", a)), "")
                tokens.append(("note", body if body.strip() else notes.get(ref, "")))
            i = end
        elif value.startswith("[[", i):
            end = value.find("]]", i)
            end = len(value) if end < 0 else end + 2
            target = value[i + 2:end - 2].split("|", 1)[0].split("#", 1)[0].strip()
            if target and ":" not in target:
                tokens.append(("item", target, None))
            i = end
        elif value.startswith("<ref", i):
            close = value.find("</ref>", i)
            short = value.find("/>", i)
            i = len(value) if close < 0 and short < 0 else (short + 2 if close < 0 or 0 <= short < close else close + 6)
        else:
            i += 1
    items = []
    for k, t in enumerate(tokens):
        if t[0] != "item":
            continue
        after = []
        for u in tokens[k + 1:]:
            if u[0] != "note":
                break
            after.append(u[1])
        if any(SET_ONLY_NOTE.search(n) for n in after) or TASK_ONLY.search(t[1]):
            continue
        items.append((t[1], t[2]))
    return items


def parse(text):
    """Each Recommended equipment table on a page: {"label", "style", "slots": {SLOT: [[(page, pic)...] per rank]}}."""
    notes = named_notes(text)
    out = []
    for call in templates(text):
        params = split_params(call)
        label = re.sub(r"<[^>]+>|\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", params.get("style", "")).strip()
        ranked = {}
        for key, value in params.items():
            m = PARAM.match(key)
            if not m:
                continue
            items = cell_items(value, notes)
            if items:
                ranked.setdefault(SLOTS[m.group(1)], []).append((int(m.group(2)), items))
        slots = {s: [items for _, items in sorted(ranks)] for s, ranks in ranked.items()}
        out.append({"label": label, "style": styles_of(label), "slots": slots})
    return out


def boss_name(page):
    """"Vorkath/Strategies" -> "Vorkath"; "Chambers of Xeric/Challenge Mode/Strategies" -> "Chambers of Xeric Challenge Mode"."""
    parts = [p for p in page.split("/") if p != "Strategies"]
    return " ".join(parts)


def fetch_pages():
    """Every main-namespace page that uses the template, with its wikitext."""
    titles, cont = [], {}
    while True:
        data = wiki_recipes.api(dict({"action": "query", "list": "embeddedin", "eititle": TEMPLATE, "eilimit": "500",
                                      "einamespace": "0"}, **cont))
        titles += [e["title"] for e in data["query"]["embeddedin"]]
        if "continue" not in data:
            break
        cont = data["continue"]
    pages = {}
    for k in range(0, len(titles), 50):
        batch = titles[k:k + 50]
        data = wiki_recipes.api({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                 "titles": "|".join(batch), "formatversion": "2"})
        for p in data["query"]["pages"]:
            revs = p.get("revisions") or []
            if revs:
                pages[p["title"]] = revs[0]["slots"]["main"]["content"]
        print("  boss setups: %d/%d pages" % (len(pages), len(titles)))
    return pages


# placeholders the wiki puts in inventory slots: the plugin fills them with the player's own best
PLACEHOLDERS = {"cheap food": "food", "cheap prayer": "prayer"}
HEADING = re.compile(r"^==+[^=\n]+==+\s*$", re.M)
TAB_LABEL = re.compile(r"^([^=\n|{}<\[]{2,60})=\s*$", re.M)


def parse_inventories(text):
    """Each {{Inventory}} on a page, with its {{Rune pouch}}: {"label", "style", "items": [(name or None, kind)]}.

    The style is the tabber tab it sits in ("Ranged (crossbow)="), when that tab is in the same section, else the
    style of the last equipment table before it. A slot is an item page name ("Divine ranging potion(3)") with
    kind None, or a placeholder ({{Cheap food}}, {{Cheap prayer}}) with no name and kind "food" or "prayer".
    Empty slots are skipped and each item is listed once, in slot order."""
    tables = [(m.start(), styles_of(split_params(call).get("style", "")))
              for m, call in ((m, text[m.start():_close(text, m.start()) or len(text)])
                              for m in re.finditer(r"\{\{\s*Recommended equipment\s*[|\n}]", text, re.I))]
    out = []
    for m in re.finditer(r"\{\{\s*Inventory\s*[|\n}]", text, re.I):
        start = m.start()
        end = _close(text, start) or len(text)
        section = max([h.end() for h in HEADING.finditer(text, 0, start)] or [0])
        labels = [lm.group(1).strip() for lm in TAB_LABEL.finditer(text, section, start)]
        label = labels[-1] if labels else ""
        style = styles_of(label)
        if style is None and not label:
            before = [s for pos, s in tables if pos < start]
            style = before[-1] if before else None
        params = split_params(text[start:end])
        slots = sorted((int(k), v) for k, v in params.items() if k.isdigit())
        # the rune pouch that goes with it: the next one before another inventory, tab or heading
        tail = text[end:]
        stop = min([p for p in (tail.find("|-|"), tail.lower().find("{{inventory")) if p >= 0]
                   + [h.start() for h in HEADING.finditer(tail)][:1] + [len(tail)])
        pouch = re.search(r"\{\{\s*Rune pouch\s*[|\n}]", tail[:stop], re.I)
        if pouch:
            call = tail[pouch.start():_close(tail, pouch.start()) or len(tail)]
            slots += [(100 + int(k), v) for k, v in split_params(call).items() if k.isdigit()]
        items = []
        for _, value in slots:
            entry = _slot(value)
            if entry and entry not in items:
                items.append(entry)
        out.append({"label": label, "style": style, "items": items})
    return out


def _slot(value):
    """One inventory slot's (name, kind), or None when empty or unreadable."""
    value = re.sub(r"<[^>]+>", "", value).strip()
    if not value:
        return None
    m = re.match(r"\{\{\s*([^|}]+)(?:\|([^|}]*))?[^}]*\}\}", value)
    if m:
        name = m.group(1).strip()
        if name.lower() in PLACEHOLDERS:
            return (None, PLACEHOLDERS[name.lower()])
        if name.lower().startswith("plink") and m.group(2):
            return (m.group(2).strip(), None)
        return None
    link = re.match(r"\[\[([^|\]#]+)", value)
    return ((link.group(1) if link else value).strip(), None)


def page_of(name):
    """The item page an inventory name means: "Divine ranging potion(3)" -> "Divine ranging potion"."""
    return re.sub(r"\s*\(\d+\)$", "", name).strip()

#!/usr/bin/env python3
"""Add (or refresh) the Boss tab and the wiki boss setups in the existing tabs.json, leaving everything else as
it is. Faster and safer than a full generate_data.py run: it needs only the wiki's item index, RuneLite's item
variations and the pages with Recommended equipment tables, and it reuses the slayer task data already there.

Stdlib only. Usage:
  python tools/add_bosses.py            # use cached wiki data if present
  python tools/add_bosses.py --refresh  # re-download it
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_data as g  # noqa: E402


def main():
    payload = json.loads(g.OUT.read_text(encoding="utf-8"))
    rows = g.cached("items.json", g.fetch_items)
    variations = g.cached("item_variations.json", g.fetch_variations)
    wiki = g.Wiki(rows)
    res = g.Resolver(wiki, variations)

    tabs = [t for t in payload["tabs"] if t["key"] != "boss"]
    at = next(k for k, t in enumerate(tabs) if t["key"] == "movement") + 1
    tabs.insert(at, {"key": "boss", "name": "Boss", "kind": "gear", "icon": 0, "sections": []})
    payload["tabs"] = tabs
    payload["bosses"] = g.bosses(wiki, res, payload.get("slayerTasks", {}))
    if res.errors:
        print("\n".join(sorted(set(res.errors))))
        sys.exit("%d unresolved names" % len(set(res.errors)))
    g.OUT.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print("wrote %s (%d KB)" % (g.OUT, g.OUT.stat().st_size // 1024))


if __name__ == "__main__":
    main()

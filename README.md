# BiS Bank Tabs Boss

A fork of [BiS Bank Tabs](https://github.com/Dewdul/bis-bank-tabs) by Dewdul (BSD 2-Clause, see [LICENSE](LICENSE)) that adds a **Boss tab**: pick a boss and the tab lays out the wiki's recommended gear for it from what you own.

## Boss tab

- Type a boss in **Boss to gear for** (Vorkath, Zulrah, Alchemical Hydra, Nex...). Leave it blank and the tab follows your slayer task whenever it's a boss.
- The gear comes from the boss's OSRS Wiki *Strategies* page (its Recommended equipment tables). For each slot, the best item you own from the wiki's ranking takes the slot; when you own none, the plugin's own best-in-slot pick stays.
- Each style the wiki lists (melee, ranged, magic) is built, and the one you're best armed for wins, the same way the Slayer tab picks a style. What the wiki's pick replaced waits beside it.
- Items the wiki says only work as a full set (Void, Justiciar) are skipped, since the tab picks slot by slot. Off task the slayer helmet isn't forced in.
- Bosses that are slayer tasks also bring their task data: banes, needed gear (a dragonfire shield, Boots of stone), tools and potions. The wiki's special attack weapons go in the items row.
- Refresh the wiki data with `python tools/add_bosses.py --refresh`, or run the **Build** workflow on GitHub with *refresh_bosses* ticked.

---

# BiS Bank Tabs (original README)

**Your best gear for every style and skill, already laid out in your bank.**

Open the bank and it's done. Nothing to tag or set up: every tab is built from what you own and updates as your bank changes.

## Why this one

- **Best in slot from your own bank**, shaped like the equipment screen, for every combat style, Movement and every skill.
- **Best at something, not just best overall:** beside each pick, what beats it at max hit or accuracy, a one-handed option, and 600+ situational picks (banes, specs, boss gear). Hover any item to see why it's there.
- **Made for ironmen:** cheaper picks that save your best, and charge-free gear beside charged gear.
- **Alchables, Clues and Junk tabs** that sort themselves.
- **Your layout stays.** Drag items anywhere; only a new best-in-slot item takes its cell back.

## Tabs

| Tab | What's in it |
|---|---|
| **Melee, Ranged, Magic** | Best gear by slot, trade-offs, situational gear, weapons for each job, specs, ammo, potions and food. Magic also holds your runes. |
| **Movement** | Graceful (or your lightest gear), stamina potions and every teleport you own. |
| **Skills** | Each skill's outfit and tools, its supplies in level order, and what it makes at the bottom. |
| **Slayer** | Leads with the best setup and items for your current task. |
| **Alchables** | What's worth High Alchemy, highest value first. |
| **Clues** | Clues by tier, the spade, teleports, graceful, and the items emote steps ask for. |
| **Cosmetics** | Purely visual items no other tab uses. |
| **Junk** | What you could sell or drop. Never anything a tab uses or an unfinished quest needs. |

Right-click an item in Alchables or Junk to keep it off that tab.

## Settings

Turn any tab on or off, plus: trade-offs, cheaper alternatives (ironmen by default), backups per slot, how many foods, supplies and finished goods, blank rows, and skill or item tab icons.

## Good to know

- Needs the core **Bank Tags** plugin. It never writes tags onto your items.
- If you already have tabs, the first run asks whether to replace or keep them. Replaced tabs are backed up, and *Bring back replaced tabs* restores them.
- It warns you if Auto Bank Sorter, Bank Assistant, Bank Sorter or Sorted Bank is also on, since they fight over the same tabs.
- Want the details on how it picks? See [docs/DESIGN.md](docs/DESIGN.md).

## Data

Item data comes from the [Old School RuneScape Wiki](https://oldschool.runescape.wiki) under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/), bundled with the plugin. It makes no network requests.

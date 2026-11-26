"""Unit tests for boss_setups.py's wiki parsing. Usage: python -m unittest discover tools"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boss_setups  # noqa: E402

FIXTURE = (Path(__file__).resolve().parent / "fixtures" / "vorkath_strategies.wikitext").read_text(encoding="utf-8")


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.inventories = boss_setups.parse_inventories(FIXTURE)

    def test_each_tab_is_a_style(self):
        self.assertEqual([("Ranged (crossbow)", "ranged"), ("Melee", "melee")],
                         [(i["label"], i["style"]) for i in self.inventories])

    def test_slots_in_order_once_each_with_placeholders_and_the_rune_pouch(self):
        self.assertEqual([("Diamond dragon bolts (e)", None), ("Divine ranging potion(3)", None),
                          ("Extended super antifire(2)", None), ("Zaryte crossbow", None), (None, "prayer"),
                          ("Cooked karambwan", None), (None, "food"), ("Divine rune pouch", None),
                          ("Law rune", None), ("Dust rune", None), ("Chaos rune", None)],
                         self.inventories[0]["items"])

    def test_plinks_and_pages(self):
        self.assertIn(("Super restore(4)", None), self.inventories[1]["items"])
        self.assertEqual("Divine ranging potion", boss_setups.page_of("Divine ranging potion(3)"))
        self.assertEqual("Diamond dragon bolts (e)", boss_setups.page_of("Diamond dragon bolts (e)"))


class ParseTest(unittest.TestCase):
    def setUp(self):
        self.tables = boss_setups.parse(FIXTURE)

    def test_each_table_is_a_style(self):
        self.assertEqual(["ranged", "melee", "ranged"], [t["style"] for t in self.tables])
        self.assertEqual("Ranged (crossbow)", self.tables[0]["label"])

    def test_ranks_in_order_with_equal_options_together(self):
        weapons = self.tables[0]["slots"]["WEAPON"]
        self.assertEqual(["Ascension crossbows"], [n for n, _ in weapons[0]])
        self.assertEqual(["Dragon hunter crossbow", "Toxic blowpipe"], [n for n, _ in weapons[1]])
        self.assertEqual(["Armadyl crossbow", "Dragon crossbow"], [n for n, _ in weapons[3]])

    def test_set_only_items_are_dropped_even_through_named_notes(self):
        head = [n for rank in self.tables[0]["slots"]["HEAD"] for n, _ in rank]
        self.assertNotIn("Void ranger helm", head)
        body = [n for rank in self.tables[0]["slots"]["BODY"] for n, _ in rank]
        self.assertEqual(["Masori body (f)"], body)

    def test_other_notes_keep_the_item(self):
        self.assertIn(("Bow of Faerdhinen", None), self.tables[0]["slots"]["WEAPON"][2])
        self.assertIn(("Serpentine helm", None), self.tables[0]["slots"]["HEAD"][1])

    def test_slayer_helmets_are_left_to_the_plugin(self):
        head = [n for rank in self.tables[1]["slots"]["HEAD"] for n, _ in rank]
        self.assertNotIn("Slayer helmet (i)", head)
        self.assertIn("Torva full helm", head)

    def test_pictured_item_is_the_fallback(self):
        self.assertIn(("Barrows helm", "Torag's helm"), self.tables[1]["slots"]["HEAD"][1])

    def test_mapped_slots(self):
        self.assertIn("AMULET", self.tables[0]["slots"])
        self.assertIn("GLOVES", self.tables[0]["slots"])
        self.assertIn("BOOTS", self.tables[0]["slots"])
        self.assertIn("SPECIAL", self.tables[0]["slots"])

    def test_styles_and_names(self):
        self.assertIsNone(boss_setups.styles_of("Hybrid (melee/magic)"))
        self.assertEqual("magic", boss_setups.styles_of("Magic (Tumeken's shadow)"))
        self.assertEqual("Vorkath", boss_setups.boss_name("Vorkath/Strategies"))


if __name__ == "__main__":
    unittest.main()

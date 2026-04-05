import random
import unittest

from games.hearts.setup import choose_table_modifier, get_trait_options, resolve_trait_choice


class TestHeartsSetup(unittest.TestCase):
    def test_trait_choices_match_terminal_options(self):
        option_numbers = [option_number for option_number, _trait in get_trait_options()]
        option_names = [trait.name for _option_number, trait in get_trait_options()]

        self.assertEqual(option_numbers, ["1", "2", "3", "4"])
        self.assertEqual(option_names, ["Thief", "Medium", "Stoic", "Duelist"])

    def test_resolve_trait_choice_accepts_number_and_name(self):
        self.assertEqual(resolve_trait_choice("1").name, "Thief")
        self.assertEqual(resolve_trait_choice("medium").name, "Medium")
        self.assertEqual(resolve_trait_choice("Stoic").name, "Stoic")
        self.assertIsNone(resolve_trait_choice(""))

    def test_choose_table_modifier_uses_shared_values(self):
        modifier = choose_table_modifier(random.Random(1))

        self.assertIn(modifier, {"Fog on the Moor", "Marked Deck"})


if __name__ == "__main__":
    unittest.main()

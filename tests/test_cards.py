import unittest

from engine.cards import Card, VALID_RANKS, VALID_SUITS, create_standard_deck
from engine.deck import Deck


class TestCard(unittest.TestCase):
    def test_card_string_formatting(self):
        card = Card(suit="hearts", rank="A")

        self.assertEqual(str(card), "A of hearts")


class TestCreateStandardDeck(unittest.TestCase):
    def test_create_standard_deck_returns_52_cards(self):
        deck = create_standard_deck()

        self.assertEqual(len(deck), 52)

    def test_all_cards_are_unique(self):
        deck = create_standard_deck()

        self.assertEqual(len(set(deck)), 52)

    def test_all_four_suits_are_present(self):
        deck = create_standard_deck()
        suits = {card.suit for card in deck}

        self.assertEqual(suits, set(VALID_SUITS))

    def test_all_thirteen_ranks_are_present(self):
        deck = create_standard_deck()
        ranks = {card.rank for card in deck}

        self.assertEqual(ranks, set(VALID_RANKS))


class TestDeck(unittest.TestCase):
    def test_default_deck_contains_52_cards(self):
        deck = Deck()

        self.assertEqual(len(deck.cards), 52)

    def test_deal_four_returns_four_hands_of_thirteen_cards(self):
        deck = Deck()

        hands = deck.deal(4)

        self.assertEqual(len(hands), 4)
        self.assertTrue(all(len(hand) == 13 for hand in hands))

    def test_dealing_preserves_all_52_unique_cards(self):
        deck = Deck()

        hands = deck.deal(4)
        dealt_cards = [card for hand in hands for card in hand]

        self.assertEqual(len(dealt_cards), 52)
        self.assertEqual(len(set(dealt_cards)), 52)

    def test_invalid_player_counts_raise_value_error(self):
        deck = Deck()

        with self.assertRaises(ValueError):
            deck.deal(0)

        with self.assertRaises(ValueError):
            deck.deal(-1)

    def test_uneven_deal_raises_value_error_for_custom_deck_size(self):
        custom_cards = [
            Card(suit="clubs", rank="2"),
            Card(suit="clubs", rank="3"),
            Card(suit="clubs", rank="4"),
            Card(suit="clubs", rank="5"),
            Card(suit="clubs", rank="6"),
        ]
        deck = Deck(cards=custom_cards)

        with self.assertRaises(ValueError):
            deck.deal(2)


if __name__ == "__main__":
    unittest.main()

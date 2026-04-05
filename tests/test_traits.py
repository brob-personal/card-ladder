import random
import unittest

from engine.cards import Card
from traits.traits import (
    DUELIST,
    MEDIUM,
    STOIC,
    THIEF,
    apply_duelist_score,
    apply_stoic_score,
    update_duelist_progress,
    use_medium_hint,
    use_thief_swap,
)


class TestThiefTrait(unittest.TestCase):
    def test_thief_swap_preserves_hand_sizes_and_total_card_count(self):
        player_hand = [
            Card(suit="clubs", rank="2"),
            Card(suit="diamonds", rank="5"),
            Card(suit="hearts", rank="9"),
        ]
        opponent_hands = [
            [Card(suit="spades", rank="K"), Card(suit="clubs", rank="7")],
            [Card(suit="hearts", rank="A"), Card(suit="diamonds", rank="J")],
            [Card(suit="spades", rank="3"), Card(suit="clubs", rank="Q")],
        ]
        original_total_cards = len(player_hand) + sum(len(hand) for hand in opponent_hands)
        chosen_card = player_hand[1]

        swap_result = use_thief_swap(
            opening_hand=player_hand,
            opponent_hands=opponent_hands,
            chosen_index=1,
            swap_used=False,
            rng=random.Random(7),
        )

        self.assertEqual(len(swap_result.player_hand), len(player_hand))
        self.assertEqual(
            len(swap_result.opponent_hand),
            len(opponent_hands[swap_result.opponent_index]),
        )
        self.assertNotIn(chosen_card, swap_result.player_hand)
        self.assertIn(swap_result.received_card, opponent_hands[swap_result.opponent_index])
        self.assertIn(swap_result.received_card, swap_result.player_hand)
        self.assertIn(chosen_card, swap_result.opponent_hand)

        updated_total_cards = len(swap_result.player_hand)
        for index, hand in enumerate(opponent_hands):
            updated_total_cards += len(swap_result.opponent_hand) if index == swap_result.opponent_index else len(hand)

        self.assertEqual(updated_total_cards, original_total_cards)


class TestMediumTrait(unittest.TestCase):
    def test_medium_returns_non_empty_hint_string(self):
        alfred_hand = [
            Card(suit="spades", rank="Q"),
            Card(suit="clubs", rank="4"),
            Card(suit="diamonds", rank="9"),
        ]

        result = use_medium_hint(
            alfred_hand=alfred_hand,
            hint_used=False,
            rng=random.Random(1),
        )

        self.assertTrue(result.hint_text)
        self.assertIsInstance(result.hint_text, str)
        self.assertTrue(result.hint_used)

    def test_medium_hint_reflects_real_hand_characteristic(self):
        alfred_hand = [
            Card(suit="spades", rank="Q"),
            Card(suit="spades", rank="A"),
            Card(suit="clubs", rank="5"),
        ]

        result = use_medium_hint(
            alfred_hand=alfred_hand,
            hint_used=False,
            rng=random.Random(2),
        )

        self.assertIn("spades", result.hint_text.lower())

    def test_medium_only_triggers_once_per_hand(self):
        alfred_hand = [
            Card(suit="hearts", rank="A"),
            Card(suit="hearts", rank="K"),
            Card(suit="hearts", rank="Q"),
            Card(suit="hearts", rank="7"),
        ]

        with self.assertRaises(ValueError):
            use_medium_hint(
                alfred_hand=alfred_hand,
                hint_used=True,
                rng=random.Random(3),
            )


class TestStoicTrait(unittest.TestCase):
    def test_one_heart_is_absorbed_correctly(self):
        taken_cards = [Card(suit="hearts", rank="5")]

        result = apply_stoic_score(
            raw_score=1,
            taken_cards=taken_cards,
            stoic_used=False,
        )

        self.assertEqual(result.adjusted_score, 0)
        self.assertEqual(result.ignored_heart_points, 1)
        self.assertTrue(result.stoic_used)

    def test_additional_hearts_still_count_normally(self):
        taken_cards = [
            Card(suit="hearts", rank="3"),
            Card(suit="hearts", rank="9"),
            Card(suit="hearts", rank="K"),
        ]

        result = apply_stoic_score(
            raw_score=3,
            taken_cards=taken_cards,
            stoic_used=False,
        )

        self.assertEqual(result.adjusted_score, 2)
        self.assertEqual(result.ignored_heart_points, 1)
        self.assertTrue(result.stoic_used)

    def test_queen_of_spades_still_counts_fully(self):
        taken_cards = [
            Card(suit="hearts", rank="7"),
            Card(suit="spades", rank="Q"),
        ]

        result = apply_stoic_score(
            raw_score=14,
            taken_cards=taken_cards,
            stoic_used=False,
        )

        self.assertEqual(result.adjusted_score, 13)
        self.assertEqual(result.ignored_heart_points, 1)
        self.assertTrue(result.stoic_used)


class TestDuelistTrait(unittest.TestCase):
    def test_streak_increments_correctly(self):
        progress = update_duelist_progress(
            consecutive_tricks_won=0,
            won_trick=True,
            bonus_used=False,
        )

        self.assertEqual(progress.consecutive_tricks_won, 1)
        self.assertFalse(progress.bonus_ready)
        self.assertFalse(progress.bonus_used)

    def test_streak_resets_when_another_player_wins(self):
        progress = update_duelist_progress(
            consecutive_tricks_won=2,
            won_trick=False,
            bonus_used=False,
        )

        self.assertEqual(progress.consecutive_tricks_won, 0)
        self.assertFalse(progress.bonus_ready)
        self.assertFalse(progress.bonus_used)

    def test_bonus_applies_once_after_three_trick_streak(self):
        progress = update_duelist_progress(
            consecutive_tricks_won=2,
            won_trick=True,
            bonus_used=False,
        )
        adjusted_score = apply_duelist_score(raw_score=7, bonus_used=progress.bonus_used)

        self.assertEqual(progress.consecutive_tricks_won, 3)
        self.assertTrue(progress.bonus_ready)
        self.assertTrue(progress.bonus_used)
        self.assertEqual(adjusted_score, 5)

    def test_bonus_does_not_apply_multiple_times_in_one_hand(self):
        progress = update_duelist_progress(
            consecutive_tricks_won=3,
            won_trick=True,
            bonus_used=True,
        )
        adjusted_score = apply_duelist_score(raw_score=7, bonus_used=progress.bonus_used)

        self.assertEqual(progress.consecutive_tricks_won, 4)
        self.assertFalse(progress.bonus_ready)
        self.assertTrue(progress.bonus_used)
        self.assertEqual(adjusted_score, 5)


if __name__ == "__main__":
    unittest.main()

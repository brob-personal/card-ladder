import random
import unittest

from engine.cards import Card
from engine.player import Player
from games.hearts.rules import handle_shooting_the_moon, score_completed_hand
from main import (
    apply_fog_on_the_moor_score,
    build_final_result_text,
    evaluate_match_result,
    reveal_marked_deck_card,
)
from traits.traits import apply_duelist_score, apply_stoic_score


class TestHeartsScoring(unittest.TestCase):
    def test_each_heart_is_worth_one_point(self):
        players = [
            Player(name="Player 1", taken_cards=[
                Card(suit="hearts", rank="2"),
                Card(suit="hearts", rank="7"),
                Card(suit="hearts", rank="K"),
            ]),
            Player(name="Player 2"),
            Player(name="Player 3"),
            Player(name="Player 4"),
        ]

        scores = score_completed_hand(players)

        self.assertEqual(scores, [3, 0, 0, 0])

    def test_queen_of_spades_is_worth_thirteen_points(self):
        players = [
            Player(name="Player 1", taken_cards=[
                Card(suit="spades", rank="Q"),
            ]),
            Player(name="Player 2"),
            Player(name="Player 3"),
            Player(name="Player 4"),
        ]

        scores = score_completed_hand(players)

        self.assertEqual(scores, [13, 0, 0, 0])

    def test_mixed_hearts_and_queen_of_spades_are_scored_together(self):
        players = [
            Player(name="Player 1", taken_cards=[
                Card(suit="hearts", rank="4"),
                Card(suit="hearts", rank="9"),
                Card(suit="spades", rank="Q"),
            ]),
            Player(name="Player 2"),
            Player(name="Player 3"),
            Player(name="Player 4"),
        ]

        scores = score_completed_hand(players)

        self.assertEqual(scores, [15, 0, 0, 0])

    def test_zero_point_hand_scores_zero(self):
        players = [
            Player(name="Player 1", taken_cards=[
                Card(suit="clubs", rank="A"),
                Card(suit="diamonds", rank="10"),
            ]),
            Player(name="Player 2"),
            Player(name="Player 3"),
            Player(name="Player 4"),
        ]

        scores = score_completed_hand(players)

        self.assertEqual(scores, [0, 0, 0, 0])

    def test_shoot_the_moon_uses_current_adjustment_logic(self):
        players = [
            Player(name="Player 1", taken_cards=[
                Card(suit="hearts", rank="2"),
                Card(suit="hearts", rank="3"),
                Card(suit="hearts", rank="4"),
                Card(suit="hearts", rank="5"),
                Card(suit="hearts", rank="6"),
                Card(suit="hearts", rank="7"),
                Card(suit="hearts", rank="8"),
                Card(suit="hearts", rank="9"),
                Card(suit="hearts", rank="10"),
                Card(suit="hearts", rank="J"),
                Card(suit="hearts", rank="Q"),
                Card(suit="hearts", rank="K"),
                Card(suit="hearts", rank="A"),
                Card(suit="spades", rank="Q"),
            ]),
            Player(name="Player 2"),
            Player(name="Player 3"),
            Player(name="Player 4"),
        ]

        scores = score_completed_hand(players)

        self.assertEqual(scores, [0, 26, 26, 26])

    def test_handle_shooting_the_moon_adjusts_scores_directly(self):
        adjusted_scores = handle_shooting_the_moon([26, 0, 0, 0])

        self.assertEqual(adjusted_scores, [0, 26, 26, 26])


class TestTraitScoreAdjustments(unittest.TestCase):
    pass


class TestTableModifiers(unittest.TestCase):
    def test_fog_on_the_moor_doubles_first_heart_point_according_to_current_design(self):
        taken_cards = [
            Card(suit="hearts", rank="6"),
            Card(suit="clubs", rank="A"),
        ]

        adjusted_score = apply_fog_on_the_moor_score(
            raw_score=1,
            taken_cards=taken_cards,
        )

        self.assertEqual(adjusted_score, 2)

    def test_marked_deck_reveals_one_random_alfred_card_without_changing_hand(self):
        alfred_hand = [
            Card(suit="clubs", rank="2"),
            Card(suit="hearts", rank="K"),
            Card(suit="spades", rank="Q"),
        ]
        state = type(
            "State",
            (),
            {
                "players": [
                    Player(name="You"),
                    Player(name="Alfred", hand=list(alfred_hand)),
                    Player(name="North"),
                    Player(name="East"),
                ]
            },
        )()

        revealed_card = reveal_marked_deck_card(state, rng=random.Random(4))

        self.assertIn(revealed_card, alfred_hand)
        self.assertEqual(state.players[1].hand, alfred_hand)


class TestAlfredGhostAdvantageLogic(unittest.TestCase):
    def test_player_wins_exactly_at_threshold(self):
        result = evaluate_match_result(player_score=20, alfred_score=30, advantage=10)

        self.assertTrue(result["player_won"])
        self.assertEqual(result["required_margin"], 10)
        self.assertEqual(result["actual_margin"], 10)

    def test_player_loses_when_finishing_less_than_ten_points_below_alfred(self):
        result = evaluate_match_result(player_score=21, alfred_score=30, advantage=10)

        self.assertFalse(result["player_won"])
        self.assertEqual(result["required_margin"], 10)
        self.assertEqual(result["actual_margin"], 9)

    def test_player_loses_when_tied_with_alfred(self):
        result = evaluate_match_result(player_score=25, alfred_score=25, advantage=10)

        self.assertFalse(result["player_won"])
        self.assertEqual(result["actual_margin"], 0)

    def test_player_loses_when_ahead_in_normal_hearts_but_not_by_required_margin(self):
        result = evaluate_match_result(player_score=18, alfred_score=20, advantage=10)

        self.assertFalse(result["player_won"])
        self.assertEqual(result["actual_margin"], 2)

    def test_regression_player_score_zero_and_alfred_score_eight_is_still_a_loss(self):
        result = evaluate_match_result(player_score=0, alfred_score=8, advantage=10)
        result_text = build_final_result_text(
            player_won=result["player_won"],
            actual_margin=result["actual_margin"],
            required_margin=result["required_margin"],
        )

        self.assertFalse(result["player_won"])
        self.assertEqual(result["actual_margin"], 8)
        self.assertIn("You lose", result_text)
        self.assertNotIn("You win", result_text)


if __name__ == "__main__":
    unittest.main()

import unittest

from engine.cards import Card, create_standard_deck
from engine.deck import Deck
from engine.game_state import GameState
from engine.player import Player
from games.hearts.logic import find_two_of_clubs_owner, get_turn_legal_plays, play_hearts_hand
from games.hearts.rules import (
    determine_trick_winner,
    handle_shooting_the_moon,
    legal_plays,
    score_completed_hand,
    update_hearts_broken,
)


class TestLegalPlays(unittest.TestCase):
    def test_first_trick_requires_leading_two_of_clubs_when_player_has_it(self):
        hand = [
            Card(suit="clubs", rank="2"),
            Card(suit="clubs", rank="K"),
            Card(suit="spades", rank="A"),
        ]

        playable_cards = get_turn_legal_plays(
            hand=hand,
            current_trick=[],
            hearts_broken=False,
            round_number=1,
        )

        self.assertEqual(playable_cards, [Card(suit="clubs", rank="2")])

    def test_player_must_follow_suit_if_able(self):
        hand = [
            Card(suit="clubs", rank="4"),
            Card(suit="hearts", rank="9"),
            Card(suit="spades", rank="Q"),
        ]
        current_trick = [Card(suit="clubs", rank="A")]

        playable_cards = legal_plays(
            hand=hand,
            current_trick=current_trick,
            hearts_broken=False,
        )

        self.assertEqual(playable_cards, [Card(suit="clubs", rank="4")])

    def test_player_may_play_off_suit_if_unable_to_follow(self):
        hand = [
            Card(suit="diamonds", rank="7"),
            Card(suit="hearts", rank="9"),
            Card(suit="spades", rank="Q"),
        ]
        current_trick = [Card(suit="clubs", rank="A")]

        playable_cards = legal_plays(
            hand=hand,
            current_trick=current_trick,
            hearts_broken=False,
        )

        self.assertEqual(playable_cards, hand)

    def test_hearts_cannot_be_led_before_they_are_broken_when_non_hearts_exist(self):
        hand = [
            Card(suit="hearts", rank="4"),
            Card(suit="hearts", rank="9"),
            Card(suit="clubs", rank="K"),
        ]

        playable_cards = legal_plays(
            hand=hand,
            current_trick=[],
            hearts_broken=False,
        )

        self.assertEqual(playable_cards, [Card(suit="clubs", rank="K")])

    def test_hearts_may_be_led_before_breaking_if_hand_only_contains_hearts(self):
        hand = [
            Card(suit="hearts", rank="4"),
            Card(suit="hearts", rank="9"),
            Card(suit="hearts", rank="K"),
        ]

        playable_cards = legal_plays(
            hand=hand,
            current_trick=[],
            hearts_broken=False,
        )

        self.assertEqual(playable_cards, hand)


class TestDetermineTrickWinner(unittest.TestCase):
    def test_highest_rank_in_lead_suit_wins_clubs_trick(self):
        trick = [
            Card(suit="clubs", rank="5"),
            Card(suit="clubs", rank="K"),
            Card(suit="clubs", rank="9"),
            Card(suit="clubs", rank="J"),
        ]

        winner_index = determine_trick_winner(trick, lead_player_index=0)

        self.assertEqual(winner_index, 1)

    def test_off_suit_cards_do_not_win_trick(self):
        trick = [
            Card(suit="diamonds", rank="10"),
            Card(suit="spades", rank="A"),
            Card(suit="diamonds", rank="Q"),
            Card(suit="hearts", rank="K"),
        ]

        winner_index = determine_trick_winner(trick, lead_player_index=0)

        self.assertEqual(winner_index, 2)

    def test_spades_trick_uses_highest_spade(self):
        trick = [
            Card(suit="spades", rank="7"),
            Card(suit="spades", rank="J"),
            Card(suit="spades", rank="A"),
            Card(suit="spades", rank="9"),
        ]

        winner_index = determine_trick_winner(trick, lead_player_index=0)

        self.assertEqual(winner_index, 2)

    def test_hearts_trick_uses_highest_heart(self):
        trick = [
            Card(suit="hearts", rank="3"),
            Card(suit="hearts", rank="10"),
            Card(suit="clubs", rank="A"),
            Card(suit="hearts", rank="Q"),
        ]

        winner_index = determine_trick_winner(trick, lead_player_index=0)

        self.assertEqual(winner_index, 3)


class TestUpdateHeartsBroken(unittest.TestCase):
    pass


class TestScoreCompletedHand(unittest.TestCase):
    pass


class TestHandleShootingTheMoon(unittest.TestCase):
    pass


class TestHeartsHandFlow(unittest.TestCase):
    def test_complete_hand_plays_all_cards_and_finishes_cleanly(self):
        players = [
            Player(name="South"),
            Player(name="West"),
            Player(name="North"),
            Player(name="East"),
        ]
        for player in players:
            player.is_human = False

        deck = Deck(cards=create_standard_deck())
        for player, hand in zip(players, deck.deal(4)):
            player.hand = list(hand)

        state = GameState(
            players=players,
            current_player_index=find_two_of_clubs_owner(players),
        )

        trick_count = 0
        played_cards: list[Card] = []

        def event_callback(event_name: str, payload: dict[str, object]) -> None:
            nonlocal trick_count
            if event_name == "trick_complete":
                trick_count += 1
                played_cards.extend(payload["played_cards"])

        result = play_hearts_hand(state, event_callback=event_callback)

        self.assertEqual(trick_count, 13)
        self.assertEqual(len(played_cards), 52)
        self.assertEqual(len(set(played_cards)), 52)
        self.assertEqual(len(result["scores"]), 4)
        self.assertTrue(all(isinstance(score, int) for score in result["scores"].values()))
        self.assertTrue(all(len(player.hand) == 0 for player in players))


if __name__ == "__main__":
    unittest.main()

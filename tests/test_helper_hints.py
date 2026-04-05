import unittest

from engine.cards import Card
from engine.game_state import GameState
from engine.player import Player
from games.hearts.controller import HeartsMatchController
from npcs.guide_robot import get_helper_banter, get_helper_hint


def make_state(
    *,
    player_hand: list[Card],
    alfred_hand: list[Card] | None = None,
    north_hand: list[Card] | None = None,
    east_hand: list[Card] | None = None,
    current_trick: list[Card] | None = None,
    current_player_index: int = 0,
    round_number: int = 2,
    hearts_broken: bool = False,
) -> GameState:
    return GameState(
        players=[
            Player(name="You", hand=list(player_hand), is_human=True),
            Player(name="Alfred", hand=list(alfred_hand or [])),
            Player(name="North", hand=list(north_hand or [])),
            Player(name="East", hand=list(east_hand or [])),
        ],
        current_trick=list(current_trick or []),
        current_player_index=current_player_index,
        round_number=round_number,
        hearts_broken=hearts_broken,
    )


class TestHelperHints(unittest.TestCase):
    def test_hint_mentions_forced_opening_lead(self):
        state = make_state(
            player_hand=[
                Card(suit="clubs", rank="2"),
                Card(suit="clubs", rank="K"),
                Card(suit="spades", rank="A"),
            ],
            round_number=1,
        )

        hint = get_helper_hint(state)

        self.assertIn("Lead 2 of clubs", hint)

    def test_hint_mentions_follow_suit_pressure(self):
        state = make_state(
            player_hand=[
                Card(suit="clubs", rank="3"),
                Card(suit="clubs", rank="J"),
                Card(suit="hearts", rank="K"),
            ],
            current_trick=[
                Card(suit="clubs", rank="A"),
                Card(suit="hearts", rank="7"),
            ],
        )

        hint = get_helper_hint(state)

        self.assertIn("must follow clubs", hint)
        self.assertIn("heart points", hint)

    def test_hint_suggests_queen_of_spades_discard(self):
        state = make_state(
            player_hand=[
                Card(suit="spades", rank="Q"),
                Card(suit="hearts", rank="9"),
                Card(suit="diamonds", rank="4"),
            ],
            current_trick=[Card(suit="clubs", rank="K")],
        )

        hint = get_helper_hint(state)

        self.assertIn("queen of spades", hint)

    def test_hint_mentions_alfred_suit_strength_when_leading(self):
        state = make_state(
            player_hand=[
                Card(suit="clubs", rank="4"),
                Card(suit="diamonds", rank="6"),
                Card(suit="spades", rank="9"),
            ],
            alfred_hand=[
                Card(suit="spades", rank="A"),
                Card(suit="spades", rank="K"),
                Card(suit="spades", rank="Q"),
                Card(suit="spades", rank="10"),
                Card(suit="spades", rank="8"),
            ],
            hearts_broken=True,
        )

        hint = get_helper_hint(state)

        self.assertIn("Alfred seems comfortable in spades", hint)


class TestHelperBanter(unittest.TestCase):
    def test_intro_banter_is_available(self):
        banter = get_helper_banter("alfred_intro", round_number=1)

        self.assertIsNotNone(banter)
        self.assertGreater(len(banter), 0)

    def test_hearts_broken_banter_is_available(self):
        banter = get_helper_banter("hearts_broken", round_number=3)

        self.assertIsNotNone(banter)
        self.assertGreater(len(banter), 0)

    def test_close_hand_banter_is_available(self):
        banter = get_helper_banter("close_hand_result", round_number=13)

        self.assertIsNotNone(banter)
        self.assertGreater(len(banter), 0)

    def test_taunt_banter_only_appears_occasionally(self):
        self.assertIsNone(get_helper_banter("alfred_taunt", round_number=1))
        self.assertIsNotNone(get_helper_banter("alfred_taunt", round_number=2))


class TestHelperControllerIntegration(unittest.TestCase):
    def test_controller_emits_intro_helper_message_at_match_start(self):
        seen_helper_messages: list[str] = []

        def event_callback(event_name: str, payload: dict[str, object]) -> None:
            if event_name == "helper_message":
                seen_helper_messages.append(payload["text"])

        controller = HeartsMatchController(
            selected_trait_name="Thief",
            table_modifier="Fog on the Moor",
            event_callback=event_callback,
        )

        controller.start_match()

        self.assertGreaterEqual(len(seen_helper_messages), 1)
        self.assertIn(seen_helper_messages[0], get_intro_lines())

    def test_controller_help_request_returns_and_emits_hint(self):
        seen_helper_messages: list[str] = []

        def event_callback(event_name: str, payload: dict[str, object]) -> None:
            if event_name == "helper_message":
                seen_helper_messages.append(payload["text"])

        controller = HeartsMatchController(
            selected_trait_name="Thief",
            table_modifier="Fog on the Moor",
            event_callback=event_callback,
        )

        hint_text = controller.request_helper_hint()

        self.assertGreater(len(hint_text), 0)
        self.assertEqual(seen_helper_messages[-1], hint_text)


def get_intro_lines() -> list[str]:
    return [get_helper_banter("alfred_intro", round_number=index) for index in range(1, 4)]


if __name__ == "__main__":
    unittest.main()

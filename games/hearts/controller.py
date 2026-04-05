import random
from dataclasses import dataclass
from typing import Callable

from engine.cards import Card
from engine.game_state import GameState
from games.hearts.logic import (
    advance_ai_players,
    apply_turn_play,
    emit_match_start_event,
    finalize_hearts_scores,
    get_turn_legal_plays,
    setup_hearts_round,
    sort_cards,
)
from npcs.alfred import ALFRED_PROFILE
from npcs.dialogue import get_alfred_dialogue_line
from npcs.guide_robot import (
    get_helper_banter,
    get_helper_close_hand_reaction,
    get_helper_hint,
    get_helper_trick_reaction,
)
from traits.traits import (
    DUELIST,
    GAMBLER,
    MEDIUM,
    STOIC,
    THIEF,
    apply_duelist_score,
    apply_gambler_reward,
    apply_stoic_score,
    update_duelist_progress,
    use_medium_hint,
    use_thief_swap,
)


BASE_MATCH_REWARD = 10


@dataclass(frozen=True)
class HeartsMatchResult:
    raw_scores: dict[str, int]
    adjusted_scores: dict[str, int]
    player_score: int
    alfred_score: int
    player_won: bool
    required_margin: int
    actual_margin: int
    reward: int
    result_text: str


class HeartsMatchController:
    def __init__(
        self,
        *,
        human_name: str = "You",
        selected_trait_name: str = THIEF.name,
        table_modifier: str = "Marked Deck",
        ai_names: list[str] | None = None,
        event_callback=None,
        thief_swap_choice_provider: Callable[[GameState], int | None] | None = None,
        marked_deck_rng: random.Random | None = None,
    ) -> None:
        self.human_name = human_name
        self.selected_trait_name = selected_trait_name
        self.table_modifier = table_modifier
        self.ai_names = ai_names if ai_names is not None else ["Alfred", "North", "East"]
        self.event_callback = event_callback
        self.thief_swap_choice_provider = thief_swap_choice_provider
        self.marked_deck_rng = marked_deck_rng
        self.alfred_advantage = ALFRED_PROFILE["game_modifiers"]["hearts"]["score_advantage"]

        self.state = setup_hearts_round(human_name=human_name, ai_names=self.ai_names)
        self.state.players[0].traits = [selected_trait_name]
        self.started = False
        self.finished = False
        self.result: HeartsMatchResult | None = None
        self.duelist_state = {
            "consecutive_tricks_won": 0,
            "bonus_used": False,
        }
        self.seen_events = {
            "hearts_broken": False,
            "alfred_takes_points": False,
            "player_takes_points": False,
            "player_ahead": False,
            "alfred_ahead": False,
            "stoic_absorbed": False,
        }

    def start_match(self) -> None:
        if self.started:
            return

        self.started = True
        emit_match_start_event(self.state, event_callback=self._handle_engine_event)
        self._emit_intro_dialogue()
        self._apply_pre_hand_effects()
        self.advance_until_human_turn()

    def get_state(self) -> GameState:
        return self.state

    def get_legal_plays(self) -> list[Card]:
        return get_turn_legal_plays(
            hand=self.state.players[0].hand,
            current_trick=self.state.current_trick,
            hearts_broken=self.state.hearts_broken,
            round_number=self.state.round_number,
        )

    def request_helper_hint(self) -> str:
        hint_text = get_helper_hint(self.state)
        self._emit_helper_message(hint_text)
        return hint_text

    def play_human_card(self, selected_card: Card) -> None:
        if self.finished:
            raise ValueError("The hand is already complete")
        if not self.started:
            self.start_match()
        if self.state.current_player_index != 0:
            raise ValueError("It is not the human player's turn")

        playable_cards = self.get_legal_plays()
        if selected_card not in playable_cards:
            raise ValueError(f"{selected_card} is not a legal play right now")

        apply_turn_play(
            self.state,
            0,
            selected_card,
            event_callback=self._handle_engine_event,
        )
        self.advance_until_human_turn()

    def advance_until_human_turn(self) -> None:
        if self.finished:
            return

        advance_ai_players(
            self.state,
            event_callback=self._handle_engine_event,
        )
        self._finalize_if_complete()

    def _apply_pre_hand_effects(self) -> None:
        if self.selected_trait_name == THIEF.name:
            self._apply_thief_swap()
        elif self.selected_trait_name == MEDIUM.name:
            self._apply_medium_hint()

        if self.table_modifier == "Marked Deck":
            revealed_card = reveal_marked_deck_card(self.state, rng=self.marked_deck_rng)
            self._emit_system_message(f"Marked Deck: you glimpse one of Alfred's cards: {revealed_card}.")
        elif self.table_modifier == "Fog on the Moor":
            self._emit_system_message(
                "Fog on the Moor: the first heart point you take this hand will count double."
            )

    def _apply_thief_swap(self) -> None:
        if self.thief_swap_choice_provider is None:
            return

        chosen_index = self.thief_swap_choice_provider(self.state)
        if chosen_index is None:
            self._emit_system_message("Thief trait: you keep your opening hand.")
            return

        player = self.state.players[0]
        opponent_hands = [opponent.hand for opponent in self.state.players[1:]]
        swap_result = use_thief_swap(
            opening_hand=player.hand,
            opponent_hands=opponent_hands,
            chosen_index=chosen_index,
            swap_used=False,
        )
        player.hand = sort_cards(swap_result.player_hand)
        swapped_opponent = self.state.players[swap_result.opponent_index + 1]
        swapped_opponent.hand = sort_cards(swap_result.opponent_hand)
        self._emit_system_message(
            f"Thief trait: traded {swap_result.chosen_card} with {swapped_opponent.name} "
            f"and received {swap_result.received_card}."
        )

    def _apply_medium_hint(self) -> None:
        alfred_player = next(player for player in self.state.players if player.name == "Alfred")
        hint_result = use_medium_hint(
            alfred_hand=alfred_player.hand,
            hint_used=False,
        )
        self._emit_helper_message(hint_result.hint_text)

    def _handle_engine_event(self, event_name: str, payload: dict[str, object]) -> None:
        self._emit(event_name, payload)

        if event_name == "hearts_broken" and not self.seen_events["hearts_broken"]:
            self.seen_events["hearts_broken"] = True
            self._emit_alfred_dialogue("hearts_broken")
            helper_line = get_helper_banter("hearts_broken", round_number=self.state.round_number)
            if helper_line is not None:
                self._emit_helper_message(helper_line)
            return

        if event_name != "trick_complete":
            return

        players = payload["players"]
        played_cards = payload["played_cards"]
        winner = payload["winner"]
        round_number = payload["round_number"]
        human_player = next(player for player in players if player.name == self.human_name)
        alfred_player = next(player for player in players if player.name == "Alfred")
        trick_points = count_points(played_cards)

        if trick_points > 0 and winner.name == "Alfred" and not self.seen_events["alfred_takes_points"]:
            self.seen_events["alfred_takes_points"] = True
            self._emit_alfred_dialogue("alfred_takes_points")

        if trick_points > 0 and winner.name == self.human_name and not self.seen_events["player_takes_points"]:
            self.seen_events["player_takes_points"] = True
            self._emit_alfred_dialogue("player_takes_points")

        helper_line = get_helper_trick_reaction(
            winner_name=winner.name,
            human_name=self.human_name,
            played_cards=played_cards,
            round_number=round_number,
        )
        if helper_line is not None:
            self._emit_helper_message(helper_line)

        if (
            self.selected_trait_name == STOIC.name
            and winner.name == self.human_name
            and not self.seen_events["stoic_absorbed"]
            and any(card.suit == "hearts" for card in played_cards)
        ):
            self.seen_events["stoic_absorbed"] = True
            self._emit_system_message("Stoic trait: the first heart point you took will not count.")

        if self.selected_trait_name == DUELIST.name:
            duelist_progress = update_duelist_progress(
                consecutive_tricks_won=self.duelist_state["consecutive_tricks_won"],
                won_trick=winner.name == self.human_name,
                bonus_used=self.duelist_state["bonus_used"],
            )
            self.duelist_state["consecutive_tricks_won"] = duelist_progress.consecutive_tricks_won
            if duelist_progress.bonus_ready and not self.duelist_state["bonus_used"]:
                self.duelist_state["bonus_used"] = True
                self._emit_system_message(
                    "Duelist trait: three tricks in a row. Your final score will be reduced by 2."
                )

        if round_number >= 10:
            player_points = count_points(human_player.taken_cards)
            alfred_points = count_points(alfred_player.taken_cards)

            if player_points < alfred_points and not self.seen_events["player_ahead"]:
                self.seen_events["player_ahead"] = True
                self._emit_alfred_dialogue("player_ahead")
            elif alfred_points < player_points and not self.seen_events["alfred_ahead"]:
                self.seen_events["alfred_ahead"] = True
                self._emit_alfred_dialogue("alfred_ahead")

    def _finalize_if_complete(self) -> None:
        if self.finished or any(player.hand for player in self.state.players):
            return

        finalize_hearts_scores(self.state, event_callback=self._handle_engine_event)
        self.finished = True
        self.result = build_match_result(
            state=self.state,
            human_name=self.human_name,
            selected_trait_name=self.selected_trait_name,
            table_modifier=self.table_modifier,
            duelist_bonus_used=self.duelist_state["bonus_used"],
            advantage=self.alfred_advantage,
        )
        self._emit("match_result", {"result": self.result})
        helper_line = get_helper_close_hand_reaction(
            scores=self.result.adjusted_scores,
            human_name=self.human_name,
            ghost_advantage=self.alfred_advantage,
            round_number=max(1, self.state.round_number - 1),
        )
        if helper_line is not None:
            self._emit_helper_message(helper_line)
        self._emit_alfred_dialogue("victory" if self.result.player_won else "defeat")

    def _emit_intro_dialogue(self) -> None:
        self._emit_alfred_dialogue("intro")
        helper_line = get_helper_banter("alfred_intro", round_number=self.state.round_number)
        if helper_line is not None:
            self._emit_helper_message(helper_line)

    def _emit_alfred_dialogue(self, event_key: str) -> None:
        line = get_alfred_dialogue_line(event_key)
        if line:
            self._emit("alfred_dialogue", {"event_key": event_key, "line": line})

    def _emit_system_message(self, text: str) -> None:
        self._emit("system_message", {"text": text})

    def _emit_helper_message(self, text: str) -> None:
        self._emit("helper_message", {"text": text})

    def _emit(self, event_name: str, payload: dict[str, object]) -> None:
        if self.event_callback is not None:
            self.event_callback(event_name, payload)


def build_match_result(
    *,
    state: GameState,
    human_name: str,
    selected_trait_name: str,
    table_modifier: str,
    duelist_bonus_used: bool,
    advantage: int,
) -> HeartsMatchResult:
    raw_scores = {player.name: player.score for player in state.players}
    adjusted_scores = dict(raw_scores)
    human_taken_cards = next(player for player in state.players if player.name == human_name).taken_cards

    if table_modifier == "Fog on the Moor":
        adjusted_scores[human_name] = apply_fog_on_the_moor_score(
            raw_score=adjusted_scores[human_name],
            taken_cards=human_taken_cards,
        )
    if selected_trait_name == STOIC.name:
        adjusted_scores[human_name] = apply_stoic_score(
            raw_score=adjusted_scores[human_name],
            taken_cards=human_taken_cards,
            stoic_used=False,
        ).adjusted_score
    if selected_trait_name == DUELIST.name:
        adjusted_scores[human_name] = apply_duelist_score(
            raw_score=adjusted_scores[human_name],
            bonus_used=duelist_bonus_used,
        )

    player_score = adjusted_scores[human_name]
    alfred_score = adjusted_scores["Alfred"]
    result_summary = evaluate_match_result(
        player_score=player_score,
        alfred_score=alfred_score,
        advantage=advantage,
    )
    player_won = result_summary["player_won"]
    reward = apply_gambler_reward(
        BASE_MATCH_REWARD,
        player_won,
        selected_trait_name == GAMBLER.name,
    )
    result_text = build_final_result_text(
        player_won=player_won,
        actual_margin=result_summary["actual_margin"],
        required_margin=result_summary["required_margin"],
    )

    return HeartsMatchResult(
        raw_scores=raw_scores,
        adjusted_scores=adjusted_scores,
        player_score=player_score,
        alfred_score=alfred_score,
        player_won=player_won,
        required_margin=result_summary["required_margin"],
        actual_margin=result_summary["actual_margin"],
        reward=reward,
        result_text=result_text,
    )


def evaluate_match_result(player_score: int, alfred_score: int, advantage: int) -> dict[str, int | bool]:
    return {
        "player_won": player_score <= (alfred_score - advantage),
        "required_margin": advantage,
        "actual_margin": alfred_score - player_score,
    }


def build_final_result_text(player_won: bool, actual_margin: int, required_margin: int) -> str:
    if player_won:
        return (
            f"Final result: You win. You finished {actual_margin} points below Alfred, "
            f"meeting the required {required_margin}-point margin."
        )

    return (
        f"Final result: You lose. You finished {actual_margin} points below Alfred, "
        f"which did not meet the required {required_margin}-point margin."
    )


def reveal_marked_deck_card(state, rng: random.Random | None = None) -> Card:
    alfred_player = next(player for player in state.players if player.name == "Alfred")
    chooser = rng if rng is not None else random
    return chooser.choice(alfred_player.hand)


def apply_fog_on_the_moor_score(raw_score: int, taken_cards: list[Card]) -> int:
    if not any(card.suit == "hearts" for card in taken_cards):
        return raw_score
    return raw_score + 1


def count_points(cards: list[Card]) -> int:
    total = 0
    for card in cards:
        if card.suit == "hearts":
            total += 1
        elif card.suit == "spades" and card.rank == "Q":
            total += 13
    return total

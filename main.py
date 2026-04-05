import random

from engine.cards import Card
from games.hearts.logic import play_hearts_hand, setup_hearts_round, sort_cards
from npcs.alfred import ALFRED_PROFILE
from npcs.dialogue import get_alfred_dialogue_line
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


def main() -> None:
    human_name = input("Enter your name: ").strip() or "You"
    selected_trait = choose_trait()
    table_modifier = choose_table_modifier()
    alfred_advantage = ALFRED_PROFILE["game_modifiers"]["hearts"]["score_advantage"]

    print("\nMatch setup:")
    print(f"Trait: {selected_trait.name}")
    print(f"Alfred's ghost advantage: {alfred_advantage}")
    print(f"Table modifier: {table_modifier}")

    intro_line = get_alfred_dialogue_line("intro")
    print(f"\n{ALFRED_PROFILE['name']} enters the match.")
    print(ALFRED_PROFILE["description"])
    if intro_line:
        print(f'Alfred says: "{intro_line}"')

    state = setup_hearts_round(human_name=human_name, ai_names=["Alfred", "North", "East"])
    state.players[0].traits = [selected_trait.name]
    duelist_state = {
        "consecutive_tricks_won": 0,
        "bonus_used": False,
    }

    if selected_trait.name == THIEF.name:
        apply_thief_opening_swap(state)
    elif selected_trait.name == MEDIUM.name:
        apply_medium_hint(state)

    apply_table_modifier_start_effect(state, table_modifier)

    result = play_hearts_hand(
        state,
        event_callback=build_alfred_event_callback(
            state.players[0].name,
            selected_trait.name,
            duelist_state,
        ),
    )

    raw_scores = dict(result["scores"])
    if table_modifier == "Fog on the Moor":
        raw_scores[human_name] = apply_fog_on_the_moor_score(
            raw_score=raw_scores[human_name],
            taken_cards=state.players[0].taken_cards,
        )
    if selected_trait.name == STOIC.name:
        stoic_result = apply_stoic_score(
            raw_score=raw_scores[human_name],
            taken_cards=state.players[0].taken_cards,
            stoic_used=False,
        )
        raw_scores[human_name] = stoic_result.adjusted_score
    if selected_trait.name == DUELIST.name:
        raw_scores[human_name] = apply_duelist_score(
            raw_score=raw_scores[human_name],
            bonus_used=duelist_state["bonus_used"],
        )

    alfred_raw_score = raw_scores["Alfred"]
    player_raw_score = raw_scores[human_name]
    result_summary = evaluate_match_result(
        player_score=player_raw_score,
        alfred_score=alfred_raw_score,
        advantage=alfred_advantage,
    )
    required_margin = result_summary["required_margin"]
    actual_margin = result_summary["actual_margin"]
    player_won = result_summary["player_won"]

    base_reward = 10
    reward = apply_gambler_reward(base_reward, player_won, selected_trait.name == GAMBLER.name)

    print("\nMatch summary:")
    print("Raw scores:")
    for player_name, score in raw_scores.items():
        print(f"{player_name}: {score}")
    print(f"Alfred's ghost advantage: {alfred_advantage}")
    print(f"Player score: {player_raw_score}")
    print(f"Alfred score: {alfred_raw_score}")
    print(f"Required margin: {required_margin} points")
    print(f"Actual margin achieved: {actual_margin} points")

    final_result_text = build_final_result_text(
        player_won=player_won,
        actual_margin=actual_margin,
        required_margin=required_margin,
    )

    if player_won:
        print(final_result_text)
        print(f"Match reward: +{reward}")
        print_alfred_dialogue("victory")
    else:
        print(final_result_text)
        print(f"Match penalty: -{reward}")
        print_alfred_dialogue("defeat")


def choose_trait():
    trait_options = {
        "1": THIEF,
        "2": MEDIUM,
        "3": STOIC,
        "4": DUELIST,
        "thief": THIEF,
        "medium": MEDIUM,
        "stoic": STOIC,
        "duelist": DUELIST,
    }

    print("Choose one trait:")
    print("1. Thief")
    print("2. Medium")
    print("3. Stoic")
    print("4. Duelist")

    while True:
        choice = input("> ").strip()
        selected_trait = trait_options.get(choice.lower())
        if selected_trait is not None:
            print(f"Selected trait: {selected_trait.name} - {selected_trait.description}")
            return selected_trait
        print("Please enter 1-4 or type Thief, Medium, Stoic, or Duelist.")


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


def choose_table_modifier() -> str:
    return random.choice(["Fog on the Moor", "Marked Deck"])


def apply_thief_opening_swap(state) -> None:
    player = state.players[0]
    swap_used = False
    print("\nThief trait: you may swap one opening-hand card with a random card from a random opponent.")
    print("Your opening hand:")
    for index, card in enumerate(player.hand, start=1):
        print(f"  {index}. {card}")

    while True:
        choice = input("Choose a card number to swap, or press Enter to skip: ").strip()
        if choice == "":
            print("You keep your opening hand.")
            return
        if not choice.isdigit():
            print("Please enter a card number or press Enter to skip.")
            continue

        selected_index = int(choice) - 1
        if selected_index < 0 or selected_index >= len(player.hand):
            print("That card number is out of range.")
            continue

        opponent_hands = [opponent.hand for opponent in state.players[1:]]

        swap_result = use_thief_swap(
            opening_hand=player.hand,
            opponent_hands=opponent_hands,
            chosen_index=selected_index,
            swap_used=swap_used,
        )
        swap_used = swap_result.swap_used
        player.hand = sort_cards(swap_result.player_hand)
        swapped_opponent = state.players[swap_result.opponent_index + 1]
        swapped_opponent.hand = sort_cards(swap_result.opponent_hand)
        print(
            f"You traded {swap_result.chosen_card} from your opening hand with a random "
            f"card from {swapped_opponent.name}. You received {swap_result.received_card}."
        )
        return


def apply_medium_hint(state) -> None:
    alfred_player = next(player for player in state.players if player.name == "Alfred")
    hint_result = use_medium_hint(
        alfred_hand=alfred_player.hand,
        hint_used=False,
    )
    print(f"\nMedium trait: {hint_result.hint_text}")


def apply_table_modifier_start_effect(state, table_modifier: str) -> None:
    if table_modifier == "Marked Deck":
        reveal_marked_deck_card(state)
    elif table_modifier == "Fog on the Moor":
        print("Fog on the Moor: the first heart point you take this hand will count double.")


def reveal_marked_deck_card(state, rng: random.Random | None = None) -> Card:
    alfred_player = next(player for player in state.players if player.name == "Alfred")
    chooser = rng if rng is not None else random
    revealed_card = chooser.choice(alfred_player.hand)
    print(f"Marked Deck: you glimpse one of Alfred's cards: {revealed_card}.")
    return revealed_card


def apply_fog_on_the_moor_score(raw_score: int, taken_cards: list[Card]) -> int:
    if not any(card.suit == "hearts" for card in taken_cards):
        return raw_score

    print("Fog on the Moor: your first heart point counted double.")
    return raw_score + 1


def build_alfred_event_callback(human_name: str, trait_name: str, duelist_state: dict[str, int | bool]):
    seen_events = {
        "hearts_broken": False,
        "alfred_takes_points": False,
        "player_takes_points": False,
        "player_ahead": False,
        "alfred_ahead": False,
        "stoic_absorbed": False,
    }

    def on_event(event_name: str, payload: dict[str, object]) -> None:
        if event_name != "trick_complete":
            return

        players = payload["players"]
        played_cards = payload["played_cards"]
        winner = payload["winner"]
        round_number = payload["round_number"]
        human_player = next(player for player in players if player.name == human_name)
        alfred_player = next(player for player in players if player.name == "Alfred")
        trick_points = count_points(played_cards)

        if not seen_events["hearts_broken"] and any(card.suit == "hearts" for card in played_cards):
            seen_events["hearts_broken"] = True
            print_alfred_dialogue("hearts_broken")

        if trick_points > 0 and winner.name == "Alfred" and not seen_events["alfred_takes_points"]:
            seen_events["alfred_takes_points"] = True
            print_alfred_dialogue("alfred_takes_points")

        if trick_points > 0 and winner.name == human_name and not seen_events["player_takes_points"]:
            seen_events["player_takes_points"] = True
            print_alfred_dialogue("player_takes_points")

        if (
            trait_name == STOIC.name
            and winner.name == human_name
            and not seen_events["stoic_absorbed"]
            and any(card.suit == "hearts" for card in played_cards)
        ):
            seen_events["stoic_absorbed"] = True
            print("Stoic trait: the first heart point you took will not count.")

        if trait_name == DUELIST.name:
            duelist_progress = update_duelist_progress(
                consecutive_tricks_won=duelist_state["consecutive_tricks_won"],
                won_trick=winner.name == human_name,
                bonus_used=duelist_state["bonus_used"],
            )
            duelist_state["consecutive_tricks_won"] = duelist_progress.consecutive_tricks_won
            if duelist_progress.bonus_ready and not duelist_state["bonus_used"]:
                duelist_state["bonus_used"] = True
                print("Duelist trait: three tricks in a row. Your final score will be reduced by 2.")

        if round_number >= 10:
            player_points = count_points(human_player.taken_cards)
            alfred_points = count_points(alfred_player.taken_cards)

            if player_points < alfred_points and not seen_events["player_ahead"]:
                seen_events["player_ahead"] = True
                print_alfred_dialogue("player_ahead")
            elif alfred_points < player_points and not seen_events["alfred_ahead"]:
                seen_events["alfred_ahead"] = True
                print_alfred_dialogue("alfred_ahead")

    return on_event


def count_points(cards: list[Card]) -> int:
    total = 0
    for card in cards:
        if card.suit == "hearts":
            total += 1
        elif card.suit == "spades" and card.rank == "Q":
            total += 13
    return total


def apply_alfred_score_advantage(scores: dict[str, int]) -> dict[str, int]:
    adjusted_scores = dict(scores)
    alfred_bonus = ALFRED_PROFILE["game_modifiers"]["hearts"]["score_advantage"]
    adjusted_scores["Alfred"] = max(0, adjusted_scores.get("Alfred", 0) - alfred_bonus)
    return adjusted_scores


def print_alfred_dialogue(event_key: str) -> None:
    line = get_alfred_dialogue_line(event_key)
    if line:
        print(f'Alfred says: "{line}"')


if __name__ == "__main__":
    main()

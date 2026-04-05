import sys

from games.hearts.controller import (
    HeartsMatchController,
    apply_fog_on_the_moor_score,
    build_final_result_text,
    evaluate_match_result,
    reveal_marked_deck_card,
)
from games.hearts.logic import prompt_human_play
from games.hearts.setup import choose_table_modifier, get_trait_options, resolve_trait_choice
from npcs.alfred import ALFRED_PROFILE
from traits.traits import (
    GAMBLER,
    THIEF,
)
from ui.app import launch_gui_scaffold


def main() -> None:
    human_name = input("Enter your name: ").strip() or "You"
    selected_trait = choose_trait()
    table_modifier = choose_table_modifier()
    alfred_advantage = ALFRED_PROFILE["game_modifiers"]["hearts"]["score_advantage"]

    print("\nMatch setup:")
    print(f"Trait: {selected_trait.name}")
    print(f"Alfred's ghost advantage: {alfred_advantage}")
    print(f"Table modifier: {table_modifier}")

    print(f"\n{ALFRED_PROFILE['name']} enters the match.")
    print(ALFRED_PROFILE["description"])

    controller = HeartsMatchController(
        human_name=human_name,
        selected_trait_name=selected_trait.name,
        table_modifier=table_modifier,
        ai_names=["Alfred", "North", "East"],
        event_callback=build_terminal_event_callback(),
        thief_swap_choice_provider=choose_thief_swap_index if selected_trait.name == THIEF.name else None,
    )
    controller.start_match()

    while not controller.finished:
        state = controller.get_state()
        human_player = state.players[0]
        playable_cards = controller.get_legal_plays()
        selected_card = prompt_human_play(
            human_player,
            list(state.current_trick),
            playable_cards,
            help_callback=controller.request_helper_hint,
        )
        controller.play_human_card(selected_card)

    result = controller.result
    if result is None:
        raise RuntimeError("Match finished without a result summary")

    print("\nMatch summary:")
    print("Raw scores:")
    for player_name, score in result.raw_scores.items():
        print(f"{player_name}: {score}")
    print(f"Alfred's ghost advantage: {alfred_advantage}")
    print(f"Player score: {result.player_score}")
    print(f"Alfred score: {result.alfred_score}")
    print(f"Required margin: {result.required_margin} points")
    print(f"Actual margin achieved: {result.actual_margin} points")

    if result.player_won:
        print(result.result_text)
        print(f"Match reward: +{result.reward}")
    else:
        print(result.result_text)
        print(f"Match penalty: -{result.reward}")


def choose_trait():
    print("Choose one trait:")
    for option_number, trait in get_trait_options():
        print(f"{option_number}. {trait.name}")

    while True:
        choice = input("> ").strip()
        selected_trait = resolve_trait_choice(choice)
        if selected_trait is not None:
            print(f"Selected trait: {selected_trait.name} - {selected_trait.description}")
            return selected_trait
        print("Please enter 1-4 or type Thief, Medium, Stoic, or Duelist.")


def choose_thief_swap_index(state) -> int | None:
    player = state.players[0]
    print("\nThief trait: you may swap one opening-hand card with a random card from a random opponent.")
    print("Your opening hand:")
    for index, card in enumerate(player.hand, start=1):
        print(f"  {index}. {card}")

    while True:
        choice = input("Choose a card number to swap, or press Enter to skip: ").strip()
        if choice == "":
            return None
        if not choice.isdigit():
            print("Please enter a card number or press Enter to skip.")
            continue

        selected_index = int(choice) - 1
        if selected_index < 0 or selected_index >= len(player.hand):
            print("That card number is out of range.")
            continue

        return selected_index


def build_terminal_event_callback():
    def on_event(event_name: str, payload: dict[str, object]) -> None:
        if event_name == "match_start":
            print("Starting a 4-player Hearts hand.")
            print(f"{payload['current_player'].name} leads first with the 2 of clubs.\n")
            return

        if event_name == "alfred_dialogue":
            print(f'Alfred says: "{payload["line"]}"')
            return

        if event_name == "helper_message":
            print(f"Helper: {payload['text']}")
            return

        if event_name == "system_message":
            print(payload["text"])
            return

        if event_name == "trick_start":
            print(f"Trick {payload['round_number']}")
            return

        if event_name == "card_played" and not payload["player"].is_human:
            print(f"{payload['player'].name} plays {payload['card']}")
            return

        if event_name == "trick_winner":
            print(f"{payload['winner'].name} takes the trick.\n")

    return on_event


if __name__ == "__main__":
    if "--gui" in sys.argv:
        launch_gui_scaffold()
    else:
        main()

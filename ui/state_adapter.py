from engine.game_state import GameState


def get_player_names(state: GameState) -> list[str]:
    return [player.name for player in state.players]


def get_player_hand_labels(state: GameState, player_index: int = 0) -> list[str]:
    return [str(card) for card in state.players[player_index].hand]


def get_score_lines(state: GameState) -> list[str]:
    return [f"{player.name}: {player.score}" for player in state.players]


def get_score_summary_text(state: GameState) -> str:
    return "\n".join(get_score_lines(state))


def get_named_score_line(state: GameState, player_name: str) -> str:
    player = next((player for player in state.players if player.name == player_name), None)
    if player is None:
        return f"{player_name}: --"
    return f"{player.name}: {player.score}"


def get_status_panel_score_text(state: GameState) -> str:
    return "\n".join(
        [
            get_named_score_line(state, "You"),
            get_named_score_line(state, "Alfred"),
            *[
                f"{player.name}: {player.score}"
                for player in state.players
                if player.name not in {"You", "Alfred"}
            ],
        ]
    )


def get_current_trick_lines(state: GameState) -> list[str]:
    if not state.current_trick:
        return ["No cards played yet."]
    return [str(card) for card in state.current_trick]


def get_current_trick_text(state: GameState) -> str:
    return "\n".join(get_current_trick_lines(state))


def get_current_trick_display_lines(state: GameState) -> list[str]:
    if not state.current_trick:
        return ["No cards in the trick yet."]

    player_count = len(state.players)
    lead_player_index = (state.current_player_index - len(state.current_trick)) % player_count
    display_lines: list[str] = []
    for offset, card in enumerate(state.current_trick):
        player_index = (lead_player_index + offset) % player_count
        display_lines.append(f"{state.players[player_index].name}: {card}")
    return display_lines


def get_current_trick_display_text(state: GameState) -> str:
    return "\n".join(get_current_trick_display_lines(state))


def get_trait_modifier_summary(trait_name: str | None, table_modifier: str | None) -> str:
    trait_text = trait_name if trait_name else "None"
    modifier_text = table_modifier if table_modifier else "None"
    return f"Trait: {trait_text}\nModifier: {modifier_text}"


def get_match_summary_text(
    trait_name: str | None,
    table_modifier: str | None,
    ghost_advantage: int,
) -> str:
    trait_text = trait_name if trait_name else "None"
    modifier_text = table_modifier if table_modifier else "None"
    return (
        f"Trait: {trait_text}\n"
        f"Modifier: {modifier_text}\n"
        f"Ghost advantage: {ghost_advantage}"
    )


def get_status_lines(state: GameState) -> list[str]:
    hearts_status = "yes" if state.hearts_broken else "no"
    lead_suit = state.current_trick[0].suit if state.current_trick else "-"
    return [
        f"Round: {state.round_number}",
        f"Current turn: {state.current_player().name}",
        f"Lead suit: {lead_suit}",
        f"Hearts broken: {hearts_status}",
    ]


def get_turn_status_text(state: GameState) -> str:
    return "\n".join(get_status_lines(state))

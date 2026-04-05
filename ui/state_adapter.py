from engine.game_state import GameState


def get_player_names(state: GameState) -> list[str]:
    return [player.name for player in state.players]


def get_player_hand_labels(state: GameState, player_index: int = 0) -> list[str]:
    return [str(card) for card in state.players[player_index].hand]


def get_score_lines(state: GameState) -> list[str]:
    return [f"{player.name}: {player.score}" for player in state.players]


def get_score_summary_text(state: GameState) -> str:
    return "\n".join(get_score_lines(state))


def get_current_trick_lines(state: GameState) -> list[str]:
    if not state.current_trick:
        return ["No cards played yet."]
    return [str(card) for card in state.current_trick]


def get_current_trick_text(state: GameState) -> str:
    return "\n".join(get_current_trick_lines(state))


def get_trait_modifier_summary(trait_name: str | None, table_modifier: str | None) -> str:
    trait_text = trait_name if trait_name else "None"
    modifier_text = table_modifier if table_modifier else "None"
    return f"Trait: {trait_text}\nModifier: {modifier_text}"


def get_status_lines(state: GameState) -> list[str]:
    hearts_status = "yes" if state.hearts_broken else "no"
    return [
        f"Round: {state.round_number}",
        f"Current player: {state.current_player().name}",
        f"Hearts broken: {hearts_status}",
    ]


def get_turn_status_text(state: GameState) -> str:
    return "\n".join(get_status_lines(state))

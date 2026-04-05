from engine.cards import Card
from engine.player import Player


def render_hand(hand: list[Card], legal_cards: list[Card] | None = None) -> str:
    legal_set = set(legal_cards or [])
    lines = ["Your hand:"]

    for index, card in enumerate(hand, start=1):
        marker = " (legal)" if card in legal_set else ""
        lines.append(f"  {index}. {card}{marker}")

    return "\n".join(lines)


def render_current_trick(player_names: list[str], trick: list[Card], lead_player_index: int) -> str:
    if not trick:
        return "Current trick: no cards played yet"

    lines = ["Current trick:"]
    for offset, card in enumerate(trick):
        player_name = player_names[(lead_player_index + offset) % len(player_names)]
        lines.append(f"  {player_name}: {card}")

    return "\n".join(lines)


def render_scores(players: list[Player]) -> str:
    lines = ["Scores:"]
    for player in players:
        lines.append(f"  {player.name}: {player.score}")
    return "\n".join(lines)


def render_prompt(message: str) -> str:
    return f"{message}\n> "


def render_trick_header(round_number: int, hearts_broken: bool) -> str:
    hearts_status = "yes" if hearts_broken else "no"
    return f"Trick {round_number} | Hearts broken: {hearts_status}"


def render_played_card(player_name: str, card: Card) -> str:
    return f"{player_name} plays {card}"


def render_trick_winner(player_name: str) -> str:
    return f"{player_name} takes the trick."


def print_hand(hand: list[Card], legal_cards: list[Card] | None = None) -> None:
    print(render_hand(hand, legal_cards))


def print_scores(players: list[Player]) -> None:
    print(render_scores(players))

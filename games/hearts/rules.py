from engine.cards import Card, VALID_RANKS
from engine.player import Player


RANK_VALUES = {rank: index for index, rank in enumerate(VALID_RANKS, start=2)}


def legal_plays(
    hand: list[Card],
    current_trick: list[Card],
    hearts_broken: bool,
) -> list[Card]:
    if not hand:
        return []

    if current_trick:
        lead_suit = current_trick[0].suit
        matching_suit = [card for card in hand if card.suit == lead_suit]
        return matching_suit if matching_suit else list(hand)

    if hearts_broken:
        return list(hand)

    non_hearts = [card for card in hand if card.suit != "hearts"]
    return non_hearts if non_hearts else list(hand)


def determine_trick_winner(trick: list[Card], lead_player_index: int) -> int:
    if not trick:
        raise ValueError("Cannot determine a trick winner from an empty trick")

    lead_suit = trick[0].suit
    winning_offset = 0
    winning_card = trick[0]

    for offset, card in enumerate(trick[1:], start=1):
        if card.suit != lead_suit:
            continue
        if RANK_VALUES[card.rank] > RANK_VALUES[winning_card.rank]:
            winning_offset = offset
            winning_card = card

    return (lead_player_index + winning_offset) % 4


def update_hearts_broken(hearts_broken: bool, played_cards: list[Card]) -> bool:
    return hearts_broken or any(card.suit == "hearts" for card in played_cards)


def handle_shooting_the_moon(scores: list[int]) -> list[int]:
    if len(scores) != 4:
        raise ValueError("Hearts scoring expects exactly 4 players")

    if 26 not in scores:
        return list(scores)

    return [0 if score == 26 else score + 26 for score in scores]


def score_completed_hand(players: list[Player]) -> list[int]:
    if len(players) != 4:
        raise ValueError("Hearts scoring expects exactly 4 players")

    scores: list[int] = []
    for player in players:
        points = 0
        for card in player.taken_cards:
            if card.suit == "hearts":
                points += 1
            elif card.suit == "spades" and card.rank == "Q":
                points += 13
        scores.append(points)

    return handle_shooting_the_moon(scores)

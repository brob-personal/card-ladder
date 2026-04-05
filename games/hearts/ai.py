from engine.cards import Card, VALID_RANKS
from games.hearts.rules import legal_plays


RANK_VALUES = {rank: index for index, rank in enumerate(VALID_RANKS, start=2)}


def choose_card_to_play(
    hand: list[Card],
    current_trick: list[Card],
    hearts_broken: bool,
) -> Card:
    playable_cards = legal_plays(hand, current_trick, hearts_broken)
    if not playable_cards:
        raise ValueError("AI cannot choose a card from an empty hand")

    if current_trick:
        safe_cards = [card for card in playable_cards if not is_point_card(card)]
        if safe_cards:
            return highest_card(safe_cards)
        return lowest_card(playable_cards)

    non_point_cards = [card for card in playable_cards if not is_point_card(card)]
    if non_point_cards:
        return highest_card(non_point_cards)
    return lowest_card(playable_cards)


def is_point_card(card: Card) -> bool:
    return card.suit == "hearts" or (card.suit == "spades" and card.rank == "Q")


def highest_card(cards: list[Card]) -> Card:
    return max(cards, key=card_sort_key)


def lowest_card(cards: list[Card]) -> Card:
    return min(cards, key=card_sort_key)


def card_sort_key(card: Card) -> tuple[int, str]:
    return (RANK_VALUES[card.rank], card.suit)

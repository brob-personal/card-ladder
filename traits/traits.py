from dataclasses import dataclass
import random

from engine.cards import Card


@dataclass(frozen=True)
class Trait:
    name: str
    description: str


GAMBLER = Trait(
    name="Gambler",
    description="Legacy trait kept for compatibility with the current prototype flow.",
)

THIEF = Trait(
    name="Thief",
    description="Once per hand, may swap one opening-hand card with a random card from a random opponent.",
)

MEDIUM = Trait(
    name="Medium",
    description="Once per hand, may sense a small hint about Alfred's likely danger or suit tendency.",
)

STOIC = Trait(
    name="Stoic",
    description="The first heart point you take in the hand does not count toward your score.",
)

DUELIST = Trait(
    name="Duelist",
    description="If you win 3 tricks in a row, reduce your final hand score by 2 once per hand.",
)


@dataclass(frozen=True)
class ThiefSwapResult:
    player_hand: list[Card]
    opponent_hand: list[Card]
    chosen_card: Card
    received_card: Card
    opponent_index: int
    swap_used: bool


@dataclass(frozen=True)
class MediumHintResult:
    hint_text: str
    hint_used: bool


@dataclass(frozen=True)
class StoicScoreResult:
    adjusted_score: int
    ignored_heart_points: int
    stoic_used: bool


@dataclass(frozen=True)
class DuelistProgress:
    consecutive_tricks_won: int
    bonus_ready: bool
    bonus_used: bool


def apply_gambler_reward(base_reward: int, won: bool, has_gambler: bool) -> int:
    if not has_gambler:
        return base_reward

    if won:
        return base_reward * 2

    return base_reward * 4


def use_thief_swap(
    opening_hand: list[Card],
    opponent_hands: list[list[Card]],
    chosen_index: int,
    swap_used: bool,
    rng: random.Random | None = None,
) -> ThiefSwapResult:
    if swap_used:
        raise ValueError("Thief swap has already been used this hand")
    if not opening_hand:
        raise ValueError("Cannot use Thief swap with an empty hand")
    if chosen_index < 0 or chosen_index >= len(opening_hand):
        raise IndexError("chosen_index is out of range for the opening hand")
    if not opponent_hands:
        raise ValueError("Cannot use Thief swap without any opponents")

    available_opponents = [
        (index, hand) for index, hand in enumerate(opponent_hands) if hand
    ]
    if not available_opponents:
        raise ValueError("Cannot use Thief swap when opponent hands are empty")

    chooser = rng if rng is not None else random
    opponent_index, opponent_hand = chooser.choice(available_opponents)
    received_card = chooser.choice(opponent_hand)

    player_hand = list(opening_hand)
    chosen_card = player_hand[chosen_index]
    player_hand[chosen_index] = received_card

    updated_opponent_hand = list(opponent_hand)
    received_index = updated_opponent_hand.index(received_card)
    updated_opponent_hand[received_index] = chosen_card

    return ThiefSwapResult(
        player_hand=player_hand,
        opponent_hand=updated_opponent_hand,
        chosen_card=chosen_card,
        received_card=received_card,
        opponent_index=opponent_index,
        swap_used=True,
    )


def use_medium_hint(
    alfred_hand: list[Card],
    hint_used: bool,
    rng: random.Random | None = None,
) -> MediumHintResult:
    if hint_used:
        raise ValueError("Medium hint has already been used this hand")
    if not alfred_hand:
        raise ValueError("Cannot read Alfred's danger from an empty hand")

    chooser = rng if rng is not None else random
    hints: list[str] = []

    if any(card.suit == "spades" and card.rank == "Q" for card in alfred_hand):
        hints.append("A chill runs through the table. Alfred may be dangerous in spades.")

    hearts_count = sum(1 for card in alfred_hand if card.suit == "hearts")
    if hearts_count >= 4:
        hints.append("You sense Alfred is leaning toward hearts.")

    suit_counts = {
        suit: sum(1 for card in alfred_hand if card.suit == suit)
        for suit in ("clubs", "diamonds", "hearts", "spades")
    }
    strongest_suit = max(suit_counts, key=suit_counts.get)
    if suit_counts[strongest_suit] >= 4:
        hints.append(f"You sense Alfred is unusually comfortable in {strongest_suit}.")

    high_cards = [card for card in alfred_hand if card.rank in {"A", "K", "Q"}]
    if len(high_cards) >= 4:
        hints.append("You sense Alfred is holding more high danger than usual.")

    if not hints:
        hints.append("The spirits are hazy. Alfred feels balanced, but not harmless.")

    return MediumHintResult(
        hint_text=chooser.choice(hints),
        hint_used=True,
    )


def apply_stoic_score(
    raw_score: int,
    taken_cards: list[Card],
    stoic_used: bool,
) -> StoicScoreResult:
    if stoic_used:
        return StoicScoreResult(
            adjusted_score=raw_score,
            ignored_heart_points=0,
            stoic_used=True,
        )

    hearts_taken = sum(1 for card in taken_cards if card.suit == "hearts")
    if hearts_taken <= 0:
        return StoicScoreResult(
            adjusted_score=raw_score,
            ignored_heart_points=0,
            stoic_used=False,
        )

    return StoicScoreResult(
        adjusted_score=max(0, raw_score - 1),
        ignored_heart_points=1,
        stoic_used=True,
    )


def update_duelist_progress(
    consecutive_tricks_won: int,
    won_trick: bool,
    bonus_used: bool,
) -> DuelistProgress:
    if bonus_used:
        next_streak = consecutive_tricks_won + 1 if won_trick else 0
        return DuelistProgress(
            consecutive_tricks_won=next_streak,
            bonus_ready=False,
            bonus_used=True,
        )

    next_streak = consecutive_tricks_won + 1 if won_trick else 0
    bonus_ready = next_streak >= 3

    return DuelistProgress(
        consecutive_tricks_won=next_streak,
        bonus_ready=bonus_ready,
        bonus_used=bonus_ready,
    )


def apply_duelist_score(raw_score: int, bonus_used: bool) -> int:
    if not bonus_used:
        return raw_score
    return max(0, raw_score - 2)

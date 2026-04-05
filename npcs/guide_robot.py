from engine.cards import Card, VALID_RANKS
from engine.game_state import GameState
from games.hearts.logic import get_turn_legal_plays


INTRO_BANTER = [
    "Hello there. I am Pip, and I shall help keep things tidy.",
    "Welcome aboard. I have encouragement ready if the cards misbehave.",
    "Good to see you. We shall make this hand feel manageable.",
]
HEARTS_BROKEN_BANTER = [
    "There go the hearts. No panic, we can still steer this.",
    "Hearts are loose now. A little caution should carry us.",
    "The room just got pricklier. We shall stay composed.",
]
TAUNT_RESPONSE_BANTER = [
    "He does love a dramatic sentence. We can still answer with good cards.",
    "That is vintage Alfred. Let us be annoyingly steady.",
    "Very spooky of him. We shall carry on beautifully.",
]
PLAYER_SWING_BANTER = [
    "That was a lumpy trick. We can smooth the next one out.",
    "A brisk wobble, but the hand is still ours to shape.",
    "Bit of a sting there. Nothing a calm follow-up cannot mend.",
]
ALFRED_SWING_BANTER = [
    "That rattled him a little. Nicely done.",
    "A sharp swing in our favor. I approve of the flourish.",
    "That should put a crease in Alfred's waistcoat.",
]
CLOSE_HAND_BANTER = [
    "That was a close finish. We are very much in this.",
    "A narrow little ending. One cleaner trick could tilt it next time.",
    "That stayed wonderfully tight. We are close to a breakthrough.",
]

RANK_VALUES = {rank: index for index, rank in enumerate(VALID_RANKS, start=2)}
HIGH_HEART_RANKS = {"10", "J", "Q", "K", "A"}
HIGH_SPADES_RANKS = {"Q", "K", "A"}
SUIT_NAMES = {
    "clubs": "clubs",
    "diamonds": "diamonds",
    "hearts": "hearts",
    "spades": "spades",
}


def get_helper_hint(state: GameState) -> str:
    player = state.players[0]

    if not player.hand:
        return "That hand is wrapped up nicely. Let us see how the scores settled."

    if state.current_player_index != 0:
        return get_waiting_hint(state)

    playable_cards = get_turn_legal_plays(
        hand=player.hand,
        current_trick=state.current_trick,
        hearts_broken=state.hearts_broken,
        round_number=state.round_number,
    )
    if not playable_cards:
        return "Nothing to do just yet. The table should sort itself out in a moment."

    if state.current_trick:
        return get_follow_hint(state, playable_cards)

    return get_lead_hint(state, playable_cards)


def get_helper_banter(event_key: str, round_number: int = 1) -> str | None:
    if event_key == "alfred_intro":
        return choose_banter_line(INTRO_BANTER, round_number)

    if event_key == "hearts_broken":
        return choose_banter_line(HEARTS_BROKEN_BANTER, round_number)

    if event_key == "alfred_taunt":
        if round_number % 2 == 1:
            return None
        return choose_banter_line(TAUNT_RESPONSE_BANTER, round_number)

    if event_key == "player_point_swing":
        return choose_banter_line(PLAYER_SWING_BANTER, round_number)

    if event_key == "alfred_point_swing":
        return choose_banter_line(ALFRED_SWING_BANTER, round_number)

    if event_key == "close_hand_result":
        return choose_banter_line(CLOSE_HAND_BANTER, round_number)

    return None


def get_helper_trick_reaction(
    *,
    winner_name: str,
    human_name: str,
    played_cards: list[Card],
    round_number: int,
) -> str | None:
    point_value = count_trick_points(played_cards)
    if point_value <= 0:
        return None

    if winner_name == "Alfred":
        if point_value < 4:
            return get_helper_banter("alfred_taunt", round_number=round_number)
        return get_helper_banter("alfred_point_swing", round_number=round_number)

    if winner_name == human_name:
        if point_value >= 2:
            return get_helper_banter("player_point_swing", round_number=round_number)
        if point_value == 1:
            return get_helper_banter("alfred_taunt", round_number=round_number)

    return None


def get_helper_close_hand_reaction(
    *,
    scores: dict[str, int],
    human_name: str,
    ghost_advantage: int,
    round_number: int,
) -> str | None:
    player_score = scores.get(human_name)
    alfred_score = scores.get("Alfred")
    if player_score is None or alfred_score is None:
        return None

    if is_close_hand_result(player_score, alfred_score, ghost_advantage):
        return get_helper_banter("close_hand_result", round_number=max(1, round_number))

    return None


def get_waiting_hint(state: GameState) -> str:
    if not state.current_trick:
        return "A short pause here. Watch what suit gets led and keep your prickly cards in mind."

    lead_suit = state.current_trick[0].suit
    alfred_signal = get_alfred_suit_signal(state)
    if alfred_signal is not None:
        return (
            f"Alfred seems {alfred_signal['feel']} in {SUIT_NAMES[alfred_signal['suit']]}. "
            "Let us see whether he keeps pressing there."
        )

    return f"The trick is leaning toward {lead_suit}. See who looks eager to win it before you commit."


def get_follow_hint(state: GameState, playable_cards: list[Card]) -> str:
    lead_suit = state.current_trick[0].suit
    winning_card = get_current_winning_card(state.current_trick)
    point_pressure = get_point_pressure_text(state.current_trick)

    if any(card.suit == lead_suit for card in state.players[0].hand):
        low_follow = min(playable_cards, key=get_card_sort_key)
        if is_card_dangerous(low_follow):
            return (
                f"You must follow {lead_suit}. {point_pressure} "
                f"Your safest-looking follow is {low_follow}."
            )

        if winning_card is not None and rank_value(winning_card.rank) >= rank_value("Q"):
            return (
                f"You must follow {lead_suit}. {point_pressure} The trick is already climbing. "
                f"A low follow like {low_follow} may keep you out of trouble."
            )

        return f"You must follow {lead_suit}. A low card there is usually the calmest choice."

    queen_of_spades = Card(suit="spades", rank="Q")
    if queen_of_spades in playable_cards:
        return "You are free to discard here. If you fancy a tidy escape, the queen of spades is tempting."

    dangerous_heart = get_highest_card(playable_cards, suit="hearts", ranks=HIGH_HEART_RANKS)
    if dangerous_heart is not None:
        return f"You cannot follow suit. Shedding {dangerous_heart} could save a headache later."

    alfred_signal = get_alfred_suit_signal(state)
    if alfred_signal is not None:
        return (
            f"You are free to discard here. Alfred seems {alfred_signal['feel']} in "
            f"{SUIT_NAMES[alfred_signal['suit']]}, so keep that suit in mind."
        )

    return "You are free to discard here. If a card makes you uneasy, this is a gentle time to let it go."


def get_lead_hint(state: GameState, playable_cards: list[Card]) -> str:
    if state.round_number == 1 and len(playable_cards) == 1:
        return f"The rules are steering this one for you. Lead {playable_cards[0]} and settle in."

    if not state.hearts_broken and any(card.suit != "hearts" for card in state.players[0].hand):
        low_non_heart = min(
            (card for card in playable_cards if card.suit != "hearts"),
            key=get_card_sort_key,
        )
        return f"Hearts are still tucked away. A modest lead like {low_non_heart} should keep things tidy."

    dangerous_spade = get_highest_card(playable_cards, suit="spades", ranks=HIGH_SPADES_RANKS)
    if dangerous_spade is not None:
        return "Your spades look a little sharp. Leading spades may hand someone a nasty trick."

    dangerous_heart = get_highest_card(playable_cards, suit="hearts", ranks=HIGH_HEART_RANKS)
    if dangerous_heart is not None:
        return f"Those high hearts could become clingy later. If you can, lead something gentler first."

    alfred_signal = get_alfred_suit_signal(state)
    if alfred_signal is not None:
        return (
            f"Alfred seems {alfred_signal['feel']} in {SUIT_NAMES[alfred_signal['suit']]}. "
            "A different suit may make life less comfortable for him."
        )

    low_card = min(playable_cards, key=get_card_sort_key)
    return f"Nothing looks too fierce just now. A small lead like {low_card} should do nicely."


def get_alfred_suit_signal(state: GameState) -> dict[str, str] | None:
    alfred = next((player for player in state.players if player.name == "Alfred"), None)
    if alfred is None or not alfred.hand:
        return None

    suit_counts = {suit: 0 for suit in SUIT_NAMES}
    suit_strength = {suit: 0 for suit in SUIT_NAMES}
    for card in alfred.hand:
        suit_counts[card.suit] += 1
        suit_strength[card.suit] += rank_value(card.rank)

    strongest_suit = max(
        suit_counts,
        key=lambda suit: (suit_counts[suit], suit_strength[suit]),
    )
    weakest_suit = min(
        suit_counts,
        key=lambda suit: (suit_counts[suit], suit_strength[suit]),
    )

    if suit_counts[strongest_suit] >= 5 or suit_strength[strongest_suit] >= 45:
        return {"suit": strongest_suit, "feel": "comfortable"}

    if suit_counts[weakest_suit] <= 1:
        return {"suit": weakest_suit, "feel": "thin"}

    return None


def get_current_winning_card(trick: list[Card]) -> Card | None:
    if not trick:
        return None

    lead_suit = trick[0].suit
    lead_cards = [card for card in trick if card.suit == lead_suit]
    return max(lead_cards, key=get_card_sort_key)


def get_point_pressure_text(trick: list[Card]) -> str:
    if any(card.suit == "spades" and card.rank == "Q" for card in trick):
        return "The queen of spades is in the air."
    if any(card.suit == "hearts" for card in trick):
        return "There are heart points on the table."
    return "No points are showing yet."


def get_highest_card(cards: list[Card], suit: str, ranks: set[str]) -> Card | None:
    matching_cards = [card for card in cards if card.suit == suit and card.rank in ranks]
    if not matching_cards:
        return None
    return max(matching_cards, key=get_card_sort_key)


def is_card_dangerous(card: Card) -> bool:
    return (card.suit == "spades" and card.rank in HIGH_SPADES_RANKS) or (
        card.suit == "hearts" and card.rank in HIGH_HEART_RANKS
    )


def get_card_sort_key(card: Card) -> int:
    return rank_value(card.rank)


def rank_value(rank: str) -> int:
    return RANK_VALUES[rank]


def choose_banter_line(lines: list[str], round_number: int) -> str | None:
    if not lines:
        return None
    return lines[(round_number - 1) % len(lines)]


def count_trick_points(trick_cards: list[Card]) -> int:
    points = 0
    for card in trick_cards:
        if card.suit == "hearts":
            points += 1
        elif card.suit == "spades" and card.rank == "Q":
            points += 13
    return points


def is_close_hand_result(player_score: int, alfred_score: int, ghost_advantage: int) -> bool:
    raw_gap = abs(player_score - alfred_score)
    advantage_gap = abs((alfred_score - player_score) - ghost_advantage)
    return raw_gap <= 3 or advantage_gap <= 2

from engine.cards import Card, VALID_RANKS
from engine.deck import Deck
from engine.game_state import GameState
from engine.player import Player
from games.hearts.ai import choose_card_to_play
from games.hearts.rules import determine_trick_winner, legal_plays, score_completed_hand, update_hearts_broken


SUIT_ORDER = {"clubs": 0, "diamonds": 1, "spades": 2, "hearts": 3}
RANK_ORDER = {rank: index for index, rank in enumerate(VALID_RANKS)}
DEFAULT_AI_NAMES = ["Alfred", "North", "East"]


def play_hearts_round(
    human_name: str = "You",
    ai_names: list[str] | None = None,
    event_callback=None,
) -> dict[str, object]:
    state = setup_hearts_round(human_name=human_name, ai_names=ai_names)
    return play_hearts_hand(state, event_callback=event_callback)


def setup_hearts_round(human_name: str = "You", ai_names: list[str] | None = None) -> GameState:
    players = create_players(human_name, ai_names=ai_names)
    deck = Deck()
    deck.shuffle()

    for player, hand in zip(players, deck.deal(4)):
        player.hand = sort_cards(hand)
        player.taken_cards.clear()

    state = GameState(
        players=players,
        current_player_index=find_two_of_clubs_owner(players),
    )

    return state


def play_hearts_hand(state: GameState, event_callback=None) -> dict[str, object]:
    print("Starting a 4-player Hearts hand.")
    print(f"{state.current_player().name} leads first with the 2 of clubs.\n")

    while state.players[0].hand:
        play_trick(state, event_callback=event_callback)
        state.round_number += 1

    scores = score_completed_hand(state.players)
    for player, score in zip(state.players, scores):
        player.score = score

    print("Hand complete.\n")
    for player in state.players:
        print(f"{player.name}: {player.score} points")

    winning_score = min(player.score for player in state.players)
    winners = [player.name for player in state.players if player.score == winning_score]

    return {
        "scores": {player.name: player.score for player in state.players},
        "winner_names": winners,
        "players": state.players,
        "hearts_broken": state.hearts_broken,
    }


def create_players(human_name: str, ai_names: list[str] | None = None) -> list[Player]:
    opponent_names = list(ai_names) if ai_names is not None else list(DEFAULT_AI_NAMES)
    if len(opponent_names) != 3:
        raise ValueError("Hearts prototype expects exactly three AI opponent names")

    return [Player(name=human_name, is_human=True)] + [Player(name=name) for name in opponent_names]


def play_trick(state: GameState, event_callback=None) -> None:
    lead_player_index = state.current_player_index
    played_cards: list[Card] = []

    print(f"Trick {state.round_number}")
    for offset in range(4):
        player_index = (lead_player_index + offset) % 4
        player = state.players[player_index]
        current_trick = list(played_cards)
        playable_cards = get_turn_legal_plays(player.hand, current_trick, state.hearts_broken, state.round_number)

        if player.is_human:
            card = prompt_human_play(player, current_trick, playable_cards)
        else:
            card = choose_card_to_play(playable_cards, current_trick, state.hearts_broken)
            print(f"{player.name} plays {card}")

        player.hand.remove(card)
        played_cards.append(card)
        state.current_trick = list(played_cards)
        state.hearts_broken = update_hearts_broken(state.hearts_broken, [card])

    winner_index = determine_trick_winner(played_cards, lead_player_index)
    winner = state.players[winner_index]
    winner.taken_cards.extend(played_cards)
    state.current_trick = []
    state.current_player_index = winner_index

    if event_callback is not None:
        event_callback(
            "trick_complete",
            {
                "round_number": state.round_number,
                "winner": winner,
                "winner_index": winner_index,
                "played_cards": list(played_cards),
                "players": state.players,
                "hearts_broken": state.hearts_broken,
            },
        )

    print(f"{winner.name} takes the trick.\n")


def prompt_human_play(player: Player, current_trick: list[Card], playable_cards: list[Card]) -> Card:
    while True:
        print(f"{player.name}, it's your turn.")
        if current_trick:
            print(f"Lead suit: {current_trick[0].suit}")
            print(f"Current trick: {', '.join(str(card) for card in current_trick)}")
        else:
            print("You are leading this trick.")

        print("Your hand:")
        for index, card in enumerate(sort_cards(player.hand), start=1):
            marker = " (legal)" if card in playable_cards else ""
            print(f"  {index}. {card}{marker}")

        choice = input("Choose a card number to play: ").strip()
        if not choice.isdigit():
            print("Please enter a number.\n")
            continue

        selected_index = int(choice) - 1
        ordered_hand = sort_cards(player.hand)
        if selected_index < 0 or selected_index >= len(ordered_hand):
            print("That card number is out of range.\n")
            continue

        selected_card = ordered_hand[selected_index]
        if selected_card not in playable_cards:
            print("That card is not a legal play right now.\n")
            continue

        print(f"You play {selected_card}")
        return selected_card


def find_two_of_clubs_owner(players: list[Player]) -> int:
    two_of_clubs = Card(suit="clubs", rank="2")
    for index, player in enumerate(players):
        if two_of_clubs in player.hand:
            return index
    return 0


def sort_cards(cards: list[Card]) -> list[Card]:
    return sorted(cards, key=lambda card: (SUIT_ORDER[card.suit], RANK_ORDER[card.rank]))


def get_turn_legal_plays(
    hand: list[Card],
    current_trick: list[Card],
    hearts_broken: bool,
    round_number: int,
) -> list[Card]:
    playable_cards = legal_plays(hand, current_trick, hearts_broken)
    if not playable_cards:
        return []

    if round_number == 1 and not current_trick:
        two_of_clubs = Card(suit="clubs", rank="2")
        if two_of_clubs in playable_cards:
            return [two_of_clubs]

    if round_number == 1 and current_trick:
        non_point_cards = [card for card in playable_cards if not is_point_card(card)]
        if non_point_cards:
            return non_point_cards

    return playable_cards


def is_point_card(card: Card) -> bool:
    return card.suit == "hearts" or (card.suit == "spades" and card.rank == "Q")

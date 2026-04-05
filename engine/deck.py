from __future__ import annotations

import random

from engine.cards import Card, create_standard_deck


class Deck:
    def __init__(self, cards: list[Card] | None = None) -> None:
        self.cards = list(cards) if cards is not None else create_standard_deck()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self, num_players: int) -> list[list[Card]]:
        if num_players <= 0:
            raise ValueError("num_players must be greater than 0")

        if len(self.cards) % num_players != 0:
            raise ValueError(
                f"Deck with {len(self.cards)} cards cannot be evenly dealt to {num_players} players"
            )

        cards_per_player = len(self.cards) // num_players
        return [
            self.cards[index * cards_per_player : (index + 1) * cards_per_player]
            for index in range(num_players)
        ]

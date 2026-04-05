from dataclasses import dataclass, field

from engine.cards import Card
from engine.player import Player


@dataclass
class GameState:
    players: list[Player]
    current_trick: list[Card] = field(default_factory=list)
    current_player_index: int = 0
    round_number: int = 1
    hearts_broken: bool = False

    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def next_player(self) -> Player:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.current_player()

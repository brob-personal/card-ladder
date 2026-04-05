from dataclasses import dataclass, field

from engine.cards import Card


@dataclass
class Player:
    name: str
    hand: list[Card] = field(default_factory=list)
    taken_cards: list[Card] = field(default_factory=list)
    score: int = 0
    is_human: bool = False
    traits: list[str] = field(default_factory=list)

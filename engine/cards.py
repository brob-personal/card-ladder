from dataclasses import dataclass


VALID_SUITS = ("clubs", "diamonds", "hearts", "spades")
VALID_RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")


@dataclass(frozen=True)
class Card:
    suit: str
    rank: str

    def __post_init__(self) -> None:
        if self.suit not in VALID_SUITS:
            raise ValueError(f"Invalid suit: {self.suit!r}")
        if self.rank not in VALID_RANKS:
            raise ValueError(f"Invalid rank: {self.rank!r}")

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"

    def __repr__(self) -> str:
        return f"Card(suit={self.suit!r}, rank={self.rank!r})"


def create_standard_deck() -> list[Card]:
    return [Card(suit=suit, rank=rank) for suit in VALID_SUITS for rank in VALID_RANKS]

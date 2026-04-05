import random

from traits.traits import DUELIST, MEDIUM, STOIC, THIEF, Trait


HEARTS_TRAIT_OPTIONS: list[tuple[str, Trait]] = [
    ("1", THIEF),
    ("2", MEDIUM),
    ("3", STOIC),
    ("4", DUELIST),
]


def get_trait_options() -> list[tuple[str, Trait]]:
    return list(HEARTS_TRAIT_OPTIONS)


def resolve_trait_choice(choice: str) -> Trait | None:
    normalized_choice = choice.strip().lower()
    for option_number, trait in HEARTS_TRAIT_OPTIONS:
        if normalized_choice in {option_number, trait.name.lower()}:
            return trait
    return None


def choose_table_modifier(rng: random.Random | None = None) -> str:
    chooser = rng if rng is not None else random
    return chooser.choice(["Fog on the Moor", "Marked Deck"])

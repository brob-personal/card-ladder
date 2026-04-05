# Architecture

## Overview

Card Ladder is a small prototype built around a playable Hearts match against Alfred, an English ghost opponent. The codebase is intentionally lightweight: core card and turn logic live outside the UI, while traits, modifiers, and dialogue add controlled variation around the match flow.

## Project Layout

`engine/`
- Shared game primitives.
- `cards.py`: `Card` model and standard 52-card deck creation.
- `deck.py`: generic `Deck` class with shuffle and deal helpers.
- `player.py`: generic `Player` dataclass.
- `game_state.py`: reusable state container for trick-taking play.

`games/hearts/`
- Hearts-specific rules and flow.
- `rules.py`: legal plays, trick winner resolution, hearts-broken updates, and scoring.
- `ai.py`: lightweight Hearts AI that always obeys legal move rules.
- `logic.py`: main hand flow, trick progression, turn legality, and setup helpers.
- `render_text.py`: terminal-oriented text render helpers.

`npcs/`
- Alfred content and dialogue loading.
- `alfred.py`: Alfred profile data, including the ghost advantage.
- `dialogue.py`: JSON-backed dialogue lookup helpers.

`traits/`
- Trait definitions and trait-effect helpers.
- Contains the current prototype traits:
  `Thief`, `Medium`, `Stoic`, `Duelist`.

`ui/`
- UI-only code.
- `app.py`: Tkinter scaffold and interaction layer.
- `state_adapter.py`: converts `GameState` into UI-friendly strings and lists.

`tests/`
- Built-in `unittest` test suite.
- Focused unit tests for cards, Hearts rules, scoring, traits, plus a lightweight hand-flow integration test.

## Separation of Concerns

Core game logic vs UI:
- Rules, scoring, turn progression, AI, and shared game models live in `engine/` and `games/hearts/`.
- The UI should consume state and call existing helpers; it should not redefine Hearts rules.

`state_adapter` role:
- `ui/state_adapter.py` is the presentation bridge between gameplay state and the UI.
- It formats hand labels, score summaries, trick text, trait/modifier summaries, and status text.
- It should stay free of Tkinter widget code and free of rule logic.

## Main Game Loop

At a high level:
1. `main.py` selects mode: terminal play or `--gui`.
2. Hearts setup creates players, builds a deck, deals cards, and initializes `GameState`.
3. Before play begins, pre-hand systems can apply:
   - selected trait effects
   - active table modifier effects
   - Alfred intro/dialogue setup
4. A hand proceeds trick by trick:
   - legal plays are calculated
   - the human or AI chooses a card
   - cards are added to the current trick
   - the trick winner is determined
   - captured cards are stored on the winning player
5. After all 13 tricks, Hearts scoring is computed, then post-score adjustments are applied.
6. Final win/loss is determined against Alfred’s ghost-advantage rule.

## Traits and Modifiers

Traits:
- Traits are player-side modifiers implemented as explicit helper functions in `traits/traits.py`.
- They should remain small, testable, and easy to call from `main.py` or the UI layer.

Current traits:
- `Thief`: opening-hand swap with a random opponent card.
- `Medium`: one approximate hint about Alfred’s opening hand.
- `Stoic`: first heart point taken does not count.
- `Duelist`: 3 tricks in a row grants a one-time 2-point reduction.

Table modifiers:
- Table modifiers are currently lightweight match-level effects coordinated from `main.py`.
- `Fog on the Moor`: first heart point effectively counts double under the current scoring design.
- `Marked Deck`: reveals one random Alfred card at hand start.

## Alfred Ghost Advantage

Alfred has a ghost advantage of 10 points.

The final result rule is:
- player wins only if `player_score <= alfred_score - 10`

This means normal Hearts “lower score wins” is not enough by itself. The player must finish at least 10 points below Alfred.

## Safe Modification Guidelines

- Put new shared card/game primitives in `engine/`.
- Put Hearts-specific rules in `games/hearts/`, not in `main.py` or `ui/`.
- Keep Tkinter concerns in `ui/`.
- Use `state_adapter.py` for UI-facing formatting instead of embedding formatting logic deep inside widgets.
- Add focused `unittest` coverage for new logic, especially if it affects scoring, legality, or final result rules.

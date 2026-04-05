# Dev Notes

## Version

Prototype 1.1 in progress

## What Is Working Well

- Core Hearts hand flow is playable in terminal mode.
- Shared game primitives are separated from Hearts-specific rules.
- Traits and table modifiers are implemented as small, explicit helpers.
- Alfred dialogue is event-based and easy to extend through JSON content.
- A Tkinter GUI scaffold exists and now reads from real Hearts state.
- The project has a growing `unittest` suite covering cards, rules, scoring, traits, and a full-hand flow check.

## Known Quirks and Edge Cases

- The GUI currently uses a simplified direct interaction flow and does not yet mirror every terminal-mode system.
- Some match effects are coordinated in `main.py`, so the terminal flow is still the main source of truth for full prototype behavior.
- The Hearts implementation is intentionally prototype-level, not a full tournament-grade rules engine.
- GUI dialogue content is lightweight and not fully synchronized with all terminal dialogue moments.

## Recent Bug Fixes

- Alfred ghost-advantage logic was corrected so the player only wins when:
  `player_score <= alfred_score - 10`
- A regression test was added for the specific failure case:
  player `0`, Alfred `8`, advantage `10`, which must be a loss.
- The final result text now matches the actual win/loss boolean and reported margin.

## Current Limitations

- Terminal mode still owns most complete match behavior.
- GUI mode is interactive, but it is still a scaffold rather than a feature-complete frontend.
- Table modifiers are lightweight and handled explicitly rather than through a generalized system.
- Trait interactions are additive but not deeply composed through a shared runtime effect engine.

## Trait Implementation Notes

- Traits live in `traits/traits.py`.
- They are implemented as explicit helper functions, not deep class hierarchies.
- Current traits:
  - `Thief`: one opening-hand swap with a random opponent card
  - `Medium`: one approximate hint about Alfred's opening hand
  - `Stoic`: first heart point is ignored once
  - `Duelist`: one-time 2-point score reduction after a 3-trick streak
- Trait application is currently orchestrated mainly from `main.py`.

## Code Map

- `engine/cards.py`: card model and standard deck creation
- `engine/deck.py`: deck storage, shuffle, and dealing
- `engine/game_state.py`: shared trick-taking state container
- `games/hearts/rules.py`: Hearts rules, legal plays, and scoring
- `games/hearts/logic.py`: Hearts hand flow and trick progression
- `games/hearts/ai.py`: lightweight Hearts AI decisions
- `npcs/dialogue.py`: Alfred dialogue loading and event lookup
- `traits/traits.py`: trait helpers and score-effect utilities
- `ui/app.py`: Tkinter GUI scaffold and click interactions
- `ui/state_adapter.py`: UI-friendly state formatting helpers
- `main.py`: terminal flow, mode selection, and prototype orchestration

## Dialogue Trigger Notes

- Alfred dialogue content is stored in `content/alfred_dialogue.json`.
- `npcs/dialogue.py` loads the JSON and returns event-based random lines.
- Dialogue is triggered sparingly from event callbacks during play.
- Current trigger points include intro, hearts broken, point-taking moments, late-hand advantage states, and match end.

## GUI Interaction Notes

- Tkinter code lives in `ui/app.py`.
- The GUI reads from existing Hearts state and uses `ui/state_adapter.py` for display-friendly formatting.
- The UI should call existing helpers for legality and turn progression instead of redefining rules.
- Current clickable-card behavior uses existing legality checks and AI helpers to advance play.

## Next Steps

- Bring more terminal-mode systems into the GUI path cleanly.
- Add GUI-safe adapters for traits, modifiers, and end-of-hand summaries.
- Expand focused tests around GUI-facing helper logic where useful.
- Continue tightening rule/flow seams so more behavior is testable without large refactors.

## Things to Avoid

- Do not mix UI widget code with Hearts rules or scoring logic.
- Do not re-implement legality checks separately in the GUI.
- Do not introduce a large framework for traits or modifiers unless the prototype clearly needs it.
- Do not refactor unrelated gameplay code just to make one feature fit.

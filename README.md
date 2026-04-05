# Card Ladder

## Overview

Card Ladder is a character-driven card game prototype built around lightweight traits, table modifiers, and opponent personality.

## Core Concept

The current prototype focuses on a Hearts match against Alfred, an English ghost opponent. Matches are shaped by player traits, random table modifiers, and event-based dialogue.

## Current Features

- Hearts vs Alfred
- Trait system:
  `Thief`, `Medium`, `Stoic`, `Duelist`
- Table modifiers:
  `Fog on the Moor`, `Marked Deck`
- Alfred dialogue system with event-triggered lines
- Tkinter GUI mode via `--gui`
- Terminal mode
- `unittest` test suite for core logic

## Running

Terminal mode:

```bash
python main.py
```

GUI mode:

```bash
python main.py --gui
```

Tests:

```bash
python -m unittest discover -s tests
```

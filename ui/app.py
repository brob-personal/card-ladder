import tkinter as tk
from tkinter import ttk

from games.hearts.ai import choose_card_to_play
from games.hearts.logic import get_turn_legal_plays, setup_hearts_round
from games.hearts.rules import determine_trick_winner, score_completed_hand, update_hearts_broken
from ui.state_adapter import (
    get_current_trick_text,
    get_player_hand_labels,
    get_score_summary_text,
    get_trait_modifier_summary,
    get_turn_status_text,
)


def launch_gui_scaffold(
    selected_trait_name: str = "Thief",
    table_modifier: str = "Marked Deck",
) -> None:
    root = build_gui_scaffold(
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
    )
    root.mainloop()


def build_gui_scaffold(
    selected_trait_name: str = "Thief",
    table_modifier: str = "Marked Deck",
) -> tk.Tk:
    state = setup_hearts_round(human_name="You", ai_names=["Alfred", "North", "East"])
    state.players[0].traits = [selected_trait_name]

    root = tk.Tk()
    root.title("Card Ladder - Hearts vs Alfred")
    root.geometry("1100x760")
    root.minsize(960, 680)

    root.columnconfigure(0, weight=3)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=3)
    root.rowconfigure(1, weight=2)

    left_area = ttk.Frame(root, padding=12)
    left_area.grid(row=0, column=0, sticky="nsew")
    left_area.columnconfigure(0, weight=1)
    left_area.columnconfigure(1, weight=1)
    left_area.rowconfigure(1, weight=1)

    status_panel = ttk.LabelFrame(root, text="Score / Status", padding=12)
    status_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)
    status_panel.columnconfigure(0, weight=1)

    hand_panel = ttk.LabelFrame(root, text="Your Hand", padding=12)
    hand_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))
    hand_panel.columnconfigure(0, weight=1)

    alfred_panel = ttk.LabelFrame(left_area, text="Alfred", padding=12)
    alfred_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 6))
    helper_panel = ttk.LabelFrame(left_area, text="Helper Robot", padding=12)
    helper_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 6))
    dialogue_panel = ttk.LabelFrame(left_area, text="Dialogue", padding=12)
    dialogue_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
    dialogue_panel.columnconfigure(0, weight=1)
    dialogue_panel.rowconfigure(0, weight=1)

    ttk.Label(
        alfred_panel,
        text="[ Alfred Portrait ]",
        anchor="center",
        width=24,
    ).pack(fill="both", expand=True)
    ttk.Label(
        helper_panel,
        text="[ Helper Robot Portrait ]",
        anchor="center",
        width=24,
    ).pack(fill="both", expand=True)
    ttk.Label(
        helper_panel,
        text="Pip the Helper Bot",
        anchor="center",
    ).pack(pady=(8, 4))

    trait_modifier_var = tk.StringVar()
    scores_var = tk.StringVar()
    status_var = tk.StringVar()
    message_var = tk.StringVar(value="Click a card to play when it is your turn.")
    dialogue_note_var = tk.StringVar(value="Pip is ready with gentle advice whenever you need it.")

    dialogue_text = tk.Text(dialogue_panel, height=12, wrap="word")
    dialogue_text.grid(row=0, column=0, sticky="nsew")
    dialogue_text.configure(state="disabled")
    ttk.Button(
        helper_panel,
        text="Help",
        command=lambda: show_helper_hint(
            state=state,
            dialogue_note_var=dialogue_note_var,
            dialogue_text=dialogue_text,
        ),
    ).pack()

    ttk.Label(
        status_panel,
        textvariable=trait_modifier_var,
        justify="left",
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))
    ttk.Separator(status_panel, orient="horizontal").grid(row=3, column=0, sticky="ew", pady=10)
    ttk.Label(status_panel, text="Scores").grid(row=4, column=0, sticky="w")
    ttk.Label(
        status_panel,
        textvariable=scores_var,
        justify="left",
    ).grid(row=5, column=0, sticky="w", pady=(6, 0))
    ttk.Label(
        status_panel,
        textvariable=status_var,
        justify="left",
    ).grid(row=6, column=0, sticky="w", pady=(12, 0))
    ttk.Label(
        status_panel,
        textvariable=message_var,
        justify="left",
        wraplength=220,
    ).grid(row=7, column=0, sticky="w", pady=(12, 0))

    hand_buttons_frame = ttk.Frame(hand_panel)
    hand_buttons_frame.grid(row=0, column=0, sticky="ew")
    hand_buttons_frame.columnconfigure(0, weight=1)

    advance_ai_until_human_turn(state, message_var)

    refresh_ui(
        state=state,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        hand_buttons_frame=hand_buttons_frame,
        message_var=message_var,
        dialogue_note_var=dialogue_note_var,
        dialogue_text=dialogue_text,
    )

    return root


def refresh_ui(
    state,
    selected_trait_name: str,
    table_modifier: str,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    hand_buttons_frame: ttk.Frame,
    message_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    dialogue_text: tk.Text,
) -> None:
    trait_modifier_var.set(get_trait_modifier_summary(selected_trait_name, table_modifier))
    scores_var.set(get_score_summary_text(state))
    status_var.set(get_turn_status_text(state))
    render_hand_buttons(
        state=state,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        hand_buttons_frame=hand_buttons_frame,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        message_var=message_var,
        dialogue_note_var=dialogue_note_var,
        dialogue_text=dialogue_text,
    )

    refresh_dialogue_text(state, dialogue_note_var, dialogue_text)


def render_hand_buttons(
    state,
    selected_trait_name: str,
    table_modifier: str,
    hand_buttons_frame: ttk.Frame,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    message_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    dialogue_text: tk.Text,
) -> None:
    for child in hand_buttons_frame.winfo_children():
        child.destroy()

    if not state.players[0].hand:
        ttk.Label(hand_buttons_frame, text="Hand complete.").grid(row=0, column=0, sticky="w")
        return

    playable_cards = get_turn_legal_plays(
        hand=state.players[0].hand,
        current_trick=state.current_trick,
        hearts_broken=state.hearts_broken,
        round_number=state.round_number,
    )
    player_turn = state.current_player_index == 0

    for index, card_label in enumerate(get_player_hand_labels(state)):
        card = state.players[0].hand[index]
        button = ttk.Button(
            hand_buttons_frame,
            text=card_label,
            command=lambda selected_card=card: on_card_clicked(
                state=state,
                selected_card=selected_card,
                selected_trait_name=selected_trait_name,
                table_modifier=table_modifier,
                trait_modifier_var=trait_modifier_var,
                scores_var=scores_var,
                status_var=status_var,
                hand_buttons_frame=hand_buttons_frame,
                message_var=message_var,
                dialogue_note_var=dialogue_note_var,
                dialogue_text=dialogue_text,
            ),
        )
        button.grid(row=0, column=index, padx=4, pady=4, sticky="ew")
        if not player_turn or card not in playable_cards:
            button.state(["disabled"])


def on_card_clicked(
    state,
    selected_card,
    selected_trait_name: str,
    table_modifier: str,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    hand_buttons_frame: ttk.Frame,
    message_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    dialogue_text: tk.Text,
) -> None:
    if not state.players[0].hand or state.current_player_index != 0:
        message_var.set("It is not your turn.")
        return

    playable_cards = get_turn_legal_plays(
        hand=state.players[0].hand,
        current_trick=state.current_trick,
        hearts_broken=state.hearts_broken,
        round_number=state.round_number,
    )
    if selected_card not in playable_cards:
        message_var.set(f"{selected_card} is not a legal play right now.")
        return

    play_card_for_player(state, 0, selected_card)
    message_var.set(f"You played {selected_card}.")

    advance_ai_until_human_turn(state, message_var)
    if not state.players[0].hand:
        finalize_scores(state)
        message_var.set("The hand is complete.")

    refresh_ui(
        state=state,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        hand_buttons_frame=hand_buttons_frame,
        message_var=message_var,
        dialogue_note_var=dialogue_note_var,
        dialogue_text=dialogue_text,
    )


def advance_ai_until_human_turn(state, message_var: tk.StringVar) -> None:
    while state.players[0].hand and state.current_player_index != 0:
        ai_player = state.current_player()
        playable_cards = get_turn_legal_plays(
            hand=ai_player.hand,
            current_trick=state.current_trick,
            hearts_broken=state.hearts_broken,
            round_number=state.round_number,
        )
        chosen_card = choose_card_to_play(playable_cards, state.current_trick, state.hearts_broken)
        play_card_for_player(state, state.current_player_index, chosen_card)
        message_var.set(f"{ai_player.name} played {chosen_card}.")


def play_card_for_player(state, player_index: int, card) -> None:
    lead_player_index = (state.current_player_index - len(state.current_trick)) % len(state.players)
    player = state.players[player_index]
    player.hand.remove(card)
    state.current_trick.append(card)
    state.hearts_broken = update_hearts_broken(state.hearts_broken, [card])

    if len(state.current_trick) < len(state.players):
        state.current_player_index = (player_index + 1) % len(state.players)
        return

    winner_index = determine_trick_winner(state.current_trick, lead_player_index)
    winner = state.players[winner_index]
    winner.taken_cards.extend(state.current_trick)
    state.current_trick = []
    state.current_player_index = winner_index
    state.round_number += 1


def finalize_scores(state) -> None:
    scores = score_completed_hand(state.players)
    for player, score in zip(state.players, scores):
        player.score = score


def refresh_dialogue_text(state, dialogue_note_var: tk.StringVar, dialogue_text: tk.Text) -> None:
    dialogue_text.configure(state="normal")
    dialogue_text.delete("1.0", "end")
    dialogue_text.insert(
        "1.0",
        "Current trick:\n"
        f"{get_current_trick_text(state)}\n\n"
        f"Pip says:\n{dialogue_note_var.get()}",
    )
    dialogue_text.configure(state="disabled")


def show_helper_hint(state, dialogue_note_var: tk.StringVar, dialogue_text: tk.Text) -> None:
    dialogue_note_var.set(get_helper_hint(state))
    refresh_dialogue_text(state, dialogue_note_var, dialogue_text)


def get_helper_hint(state) -> str:
    player = state.players[0]

    if not player.hand:
        return "That hand is wrapped up nicely. Let us see how the scores settled."

    if state.current_player_index != 0:
        return "You can wait a moment here. Watch the trick and keep your risky cards in mind."

    playable_cards = get_turn_legal_plays(
        hand=player.hand,
        current_trick=state.current_trick,
        hearts_broken=state.hearts_broken,
        round_number=state.round_number,
    )

    if state.current_trick:
        lead_suit = state.current_trick[0].suit
        if any(card.suit == lead_suit for card in player.hand):
            return f"You can follow {lead_suit}. A lower card is often the calmer option."
        if any(card.suit == "spades" and card.rank == "Q" for card in playable_cards):
            return "You cannot follow suit. This may be a gentle time to let the queen of spades go."
        return "You are free to discard here. If a card worries you, this may be a kind moment to part with it."

    if not state.hearts_broken and any(card.suit != "hearts" for card in player.hand):
        return "Hearts are still unbroken, so a low non-heart lead should keep things tidy."

    if any(card.suit == "hearts" and card.rank in {"Q", "K", "A"} for card in playable_cards):
        return "Your hearts look a little sharp. Try not to take control unless you mean to."

    return "Nothing looks too dangerous just now. A small, steady play should do nicely."

import tkinter as tk
from tkinter import ttk

from engine.cards import Card
from games.hearts.controller import HeartsMatchController
from games.hearts.setup import choose_table_modifier, get_trait_options, resolve_trait_choice
from npcs.alfred import ALFRED_PROFILE
from ui.state_adapter import (
    get_current_trick_display_text,
    get_match_summary_text,
    get_player_hand_labels,
    get_status_panel_score_text,
    get_turn_status_text,
)


def launch_gui_scaffold() -> None:
    root = build_gui_scaffold()
    root.mainloop()


def build_gui_scaffold() -> tk.Tk:
    root = tk.Tk()
    root.title("Card Ladder - Hearts vs Alfred")
    root.geometry("1100x760")
    root.minsize(960, 680)
    show_match_setup_screen(root)
    return root


def show_match_setup_screen(root: tk.Tk) -> None:
    clear_root(root)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    outer = ttk.Frame(root, padding=24)
    outer.grid(row=0, column=0, sticky="nsew")
    outer.columnconfigure(0, weight=1)

    setup_panel = ttk.LabelFrame(outer, text="Hearts Match Setup", padding=18)
    setup_panel.grid(row=0, column=0, sticky="n", pady=24)
    setup_panel.columnconfigure(0, weight=1)

    name_var = tk.StringVar()
    trait_var = tk.StringVar()
    error_var = tk.StringVar()

    ttk.Label(setup_panel, text="Player Name").grid(row=0, column=0, sticky="w")
    name_entry = ttk.Entry(setup_panel, textvariable=name_var, width=28)
    name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 12))

    ttk.Label(setup_panel, text="Choose Your Trait").grid(row=2, column=0, sticky="w")
    trait_frame = ttk.Frame(setup_panel)
    trait_frame.grid(row=3, column=0, sticky="ew", pady=(6, 10))
    trait_frame.columnconfigure(0, weight=1)

    for row_index, (option_number, trait) in enumerate(get_trait_options()):
        ttk.Radiobutton(
            trait_frame,
            text=f"{option_number}. {trait.name} - {trait.description}",
            variable=trait_var,
            value=trait.name,
        ).grid(row=row_index, column=0, sticky="w", pady=2)

    ttk.Label(
        setup_panel,
        textvariable=error_var,
        foreground="#8b0000",
        wraplength=520,
        justify="left",
    ).grid(row=4, column=0, sticky="w")

    ttk.Button(
        setup_panel,
        text="Start Match",
        command=lambda: start_match_from_setup(
            root=root,
            player_name=name_var.get(),
            selected_trait_value=trait_var.get(),
            error_var=error_var,
        ),
    ).grid(row=5, column=0, sticky="e", pady=(14, 0))

    name_entry.focus_set()


def start_match_from_setup(
    *,
    root: tk.Tk,
    player_name: str,
    selected_trait_value: str,
    error_var: tk.StringVar,
) -> None:
    cleaned_name = player_name.strip()
    if not cleaned_name:
        error_var.set("Enter your name before starting the match.")
        return

    selected_trait = resolve_trait_choice(selected_trait_value)
    if selected_trait is None:
        error_var.set("Choose one trait to continue.")
        return

    show_gameplay_screen(
        root=root,
        human_name=cleaned_name,
        selected_trait_name=selected_trait.name,
        table_modifier=choose_table_modifier(),
    )


def show_gameplay_screen(
    *,
    root: tk.Tk,
    human_name: str,
    selected_trait_name: str,
    table_modifier: str,
) -> None:
    clear_root(root)
    controller = HeartsMatchController(
        human_name=human_name,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        ai_names=["Alfred", "North", "East"],
        thief_swap_choice_provider=build_gui_thief_swap_provider(root)
        if selected_trait_name == "Thief"
        else None,
    )
    state = controller.get_state()

    root.columnconfigure(0, weight=3)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=3)
    root.rowconfigure(1, weight=2)

    left_area = ttk.Frame(root, padding=12)
    left_area.grid(row=0, column=0, sticky="nsew")
    left_area.columnconfigure(0, weight=1)
    left_area.columnconfigure(1, weight=1)
    left_area.rowconfigure(1, weight=0)
    left_area.rowconfigure(2, weight=1)

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
    current_trick_panel = ttk.LabelFrame(left_area, text="Current Trick", padding=12)
    current_trick_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 6))
    current_trick_panel.columnconfigure(0, weight=1)
    event_log_panel = ttk.LabelFrame(left_area, text="Event Log", padding=12)
    event_log_panel.grid(row=2, column=0, columnspan=2, sticky="nsew")
    event_log_panel.columnconfigure(0, weight=1)
    event_log_panel.rowconfigure(0, weight=1)

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
    current_trick_var = tk.StringVar(value=get_current_trick_display_text(state))
    ghost_advantage = ALFRED_PROFILE["game_modifiers"]["hearts"]["score_advantage"]
    alfred_dialogue_var = tk.StringVar(value="Good evening. Shall we begin?")
    message_var = tk.StringVar(value="Setting up the hand.")
    dialogue_note_var = tk.StringVar(value="Pip is ready with gentle advice whenever you need it.")
    event_log_lines: list[str] = []

    ttk.Label(
        current_trick_panel,
        textvariable=current_trick_var,
        justify="left",
        anchor="w",
    ).grid(row=0, column=0, sticky="w")

    event_log_text = tk.Text(event_log_panel, height=14, wrap="word")
    event_log_text.grid(row=0, column=0, sticky="nsew")
    event_log_text.configure(state="disabled")
    ttk.Button(
        helper_panel,
        text="Help",
        command=lambda: request_helper_hint(
            controller=controller,
            alfred_dialogue_var=alfred_dialogue_var,
            dialogue_note_var=dialogue_note_var,
            message_var=message_var,
            current_trick_var=current_trick_var,
            event_log_lines=event_log_lines,
            event_log_text=event_log_text,
        ),
    ).pack()

    ttk.Label(status_panel, text="Match").grid(row=0, column=0, sticky="w")
    ttk.Label(
        status_panel,
        textvariable=trait_modifier_var,
        justify="left",
        wraplength=220,
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))
    ttk.Separator(status_panel, orient="horizontal").grid(row=2, column=0, sticky="ew", pady=10)
    ttk.Label(status_panel, text="Scores").grid(row=3, column=0, sticky="w")
    ttk.Label(
        status_panel,
        textvariable=scores_var,
        justify="left",
    ).grid(row=4, column=0, sticky="w", pady=(4, 0))
    ttk.Separator(status_panel, orient="horizontal").grid(row=5, column=0, sticky="ew", pady=10)
    ttk.Label(status_panel, text="Turn").grid(row=6, column=0, sticky="w")
    ttk.Label(
        status_panel,
        textvariable=status_var,
        justify="left",
        wraplength=220,
    ).grid(row=7, column=0, sticky="w", pady=(4, 0))

    hand_buttons_frame = ttk.Frame(hand_panel)
    hand_buttons_frame.grid(row=0, column=0, sticky="ew")
    hand_buttons_frame.columnconfigure(0, weight=1)

    gui_event_callback = build_gui_event_callback(
        alfred_dialogue_var=alfred_dialogue_var,
        dialogue_note_var=dialogue_note_var,
        message_var=message_var,
        event_log_lines=event_log_lines,
    )
    controller.event_callback = gui_event_callback
    controller.start_match()
    message_var.set("Click a legal card to play when it is your turn.")

    refresh_ui(
        controller=controller,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        ghost_advantage=ghost_advantage,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        current_trick_var=current_trick_var,
        hand_buttons_frame=hand_buttons_frame,
        alfred_dialogue_var=alfred_dialogue_var,
        message_var=message_var,
        dialogue_note_var=dialogue_note_var,
        event_log_lines=event_log_lines,
        event_log_text=event_log_text,
    )


def clear_root(root: tk.Tk) -> None:
    for child in root.winfo_children():
        child.destroy()


def build_gui_thief_swap_provider(root: tk.Tk):
    def choose_swap_index(state) -> int | None:
        player = state.players[0]
        selection = {"index": None}
        dialog = tk.Toplevel(root)
        dialog.title("Thief Trait")
        dialog.transient(root)
        dialog.grab_set()

        dialog.columnconfigure(0, weight=1)
        ttk.Label(
            dialog,
            text="Choose one opening-hand card to trade, or skip the swap.",
            wraplength=360,
            justify="left",
            padding=12,
        ).grid(row=0, column=0, sticky="w")

        cards_frame = ttk.Frame(dialog, padding=(12, 0, 12, 12))
        cards_frame.grid(row=1, column=0, sticky="nsew")
        cards_frame.columnconfigure(0, weight=1)

        for row_index, card in enumerate(player.hand):
            ttk.Button(
                cards_frame,
                text=str(card),
                command=lambda selected_index=row_index: finalize_thief_swap_choice(
                    dialog=dialog,
                    selection=selection,
                    selected_index=selected_index,
                ),
            ).grid(row=row_index, column=0, sticky="ew", pady=2)

        ttk.Button(
            dialog,
            text="Skip Swap",
            command=lambda: finalize_thief_swap_choice(
                dialog=dialog,
                selection=selection,
                selected_index=None,
            ),
        ).grid(row=2, column=0, sticky="e", padx=12, pady=(0, 12))

        dialog.protocol(
            "WM_DELETE_WINDOW",
            lambda: finalize_thief_swap_choice(
                dialog=dialog,
                selection=selection,
                selected_index=None,
            ),
        )
        root.wait_window(dialog)
        return selection["index"]

    return choose_swap_index


def finalize_thief_swap_choice(
    *,
    dialog: tk.Toplevel,
    selection: dict[str, int | None],
    selected_index: int | None,
) -> None:
    selection["index"] = selected_index
    dialog.destroy()


def refresh_ui(
    controller: HeartsMatchController,
    selected_trait_name: str,
    table_modifier: str,
    ghost_advantage: int,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    current_trick_var: tk.StringVar,
    hand_buttons_frame: ttk.Frame,
    alfred_dialogue_var: tk.StringVar,
    message_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    event_log_lines: list[str],
    event_log_text: tk.Text,
) -> None:
    state = controller.get_state()
    trait_modifier_var.set(
        get_match_summary_text(selected_trait_name, table_modifier, ghost_advantage)
    )
    scores_var.set(get_status_panel_score_text(state))
    status_var.set(get_turn_status_text(state))
    current_trick_var.set(get_current_trick_display_text(state))
    render_hand_buttons(
        controller=controller,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        ghost_advantage=ghost_advantage,
        hand_buttons_frame=hand_buttons_frame,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        current_trick_var=current_trick_var,
        message_var=message_var,
        alfred_dialogue_var=alfred_dialogue_var,
        dialogue_note_var=dialogue_note_var,
        event_log_lines=event_log_lines,
        event_log_text=event_log_text,
    )

    render_event_log(
        alfred_note=alfred_dialogue_var.get(),
        helper_note=dialogue_note_var.get(),
        system_note=message_var.get(),
        event_log_lines=event_log_lines,
        event_log_text=event_log_text,
    )


def render_hand_buttons(
    controller: HeartsMatchController,
    selected_trait_name: str,
    table_modifier: str,
    ghost_advantage: int,
    hand_buttons_frame: ttk.Frame,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    current_trick_var: tk.StringVar,
    message_var: tk.StringVar,
    alfred_dialogue_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    event_log_lines: list[str],
    event_log_text: tk.Text,
) -> None:
    state = controller.get_state()
    playable_cards = controller.get_legal_plays() if state.current_player_index == 0 else []
    for child in hand_buttons_frame.winfo_children():
        child.destroy()

    if not state.players[0].hand:
        ttk.Label(hand_buttons_frame, text="Hand complete.").grid(row=0, column=0, sticky="w")
        return

    player_turn = state.current_player_index == 0

    for index, card_label in enumerate(get_player_hand_labels(state)):
        card = state.players[0].hand[index]
        is_legal_card = card in playable_cards if player_turn else False
        button_label = card_label
        if player_turn and not is_legal_card:
            button_label = f"{card_label} (illegal)"
        button = ttk.Button(
            hand_buttons_frame,
            text=button_label,
            command=lambda selected_card=card: on_card_clicked(
                controller=controller,
                selected_card=selected_card,
                selected_trait_name=selected_trait_name,
                table_modifier=table_modifier,
                ghost_advantage=ghost_advantage,
                trait_modifier_var=trait_modifier_var,
                scores_var=scores_var,
                status_var=status_var,
                current_trick_var=current_trick_var,
                hand_buttons_frame=hand_buttons_frame,
                message_var=message_var,
                alfred_dialogue_var=alfred_dialogue_var,
                dialogue_note_var=dialogue_note_var,
                event_log_lines=event_log_lines,
                event_log_text=event_log_text,
            ),
        )
        button.grid(row=0, column=index, padx=4, pady=4, sticky="ew")
        if not player_turn:
            button.state(["disabled"])


def on_card_clicked(
    controller: HeartsMatchController,
    selected_card,
    selected_trait_name: str,
    table_modifier: str,
    ghost_advantage: int,
    trait_modifier_var: tk.StringVar,
    scores_var: tk.StringVar,
    status_var: tk.StringVar,
    current_trick_var: tk.StringVar,
    hand_buttons_frame: ttk.Frame,
    message_var: tk.StringVar,
    alfred_dialogue_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    event_log_lines: list[str],
    event_log_text: tk.Text,
) -> None:
    state = controller.get_state()
    if not state.players[0].hand or state.current_player_index != 0:
        message_var.set("It is not your turn.")
        render_event_log(
            alfred_note=alfred_dialogue_var.get(),
            helper_note=dialogue_note_var.get(),
            system_note=message_var.get(),
            event_log_lines=event_log_lines,
            event_log_text=event_log_text,
        )
        return

    playable_cards = controller.get_legal_plays()
    if selected_card not in playable_cards:
        message_var.set(build_illegal_play_message(state, selected_card, playable_cards))
        render_event_log(
            alfred_note=alfred_dialogue_var.get(),
            helper_note=dialogue_note_var.get(),
            system_note=message_var.get(),
            event_log_lines=event_log_lines,
            event_log_text=event_log_text,
        )
        return

    controller.play_human_card(selected_card)
    state = controller.get_state()
    if controller.finished:
        message_var.set(f"Played: {selected_card}. Hand complete.")
    elif state.current_player_index == 0:
        message_var.set(f"Played: {selected_card}. Your turn again.")
    else:
        message_var.set(f"Played: {selected_card}. Waiting for the table.")

    refresh_ui(
        controller=controller,
        selected_trait_name=selected_trait_name,
        table_modifier=table_modifier,
        ghost_advantage=ghost_advantage,
        trait_modifier_var=trait_modifier_var,
        scores_var=scores_var,
        status_var=status_var,
        current_trick_var=current_trick_var,
        hand_buttons_frame=hand_buttons_frame,
        alfred_dialogue_var=alfred_dialogue_var,
        message_var=message_var,
        dialogue_note_var=dialogue_note_var,
        event_log_lines=event_log_lines,
        event_log_text=event_log_text,
    )


def build_gui_event_callback(
    alfred_dialogue_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    message_var: tk.StringVar,
    event_log_lines: list[str],
):
    def on_event(event_name: str, payload: dict[str, object]) -> None:
        if event_name == "match_start":
            append_event_log_line(
                event_log_lines,
                f"System: Match start. {payload['current_player'].name} leads.",
            )
            return

        if event_name == "alfred_dialogue":
            alfred_dialogue_var.set(payload["line"])
            append_event_log_line(event_log_lines, f"Alfred: {payload['line']}")
            return

        if event_name == "helper_message":
            dialogue_note_var.set(payload["text"])
            append_event_log_line(event_log_lines, f"Helper: {payload['text']}")
            return

        if event_name == "system_message":
            message_var.set(payload["text"])
            append_event_log_line(event_log_lines, f"System: {payload['text']}")
            return

        if event_name == "trick_start":
            append_event_log_line(
                event_log_lines,
                f"System: Trick {payload['round_number']} begins.",
            )
            return

        if event_name == "card_played":
            append_event_log_line(
                event_log_lines,
                f"{payload['player'].name}: played {payload['card']}",
            )
            return

        if event_name == "hearts_broken":
            append_event_log_line(event_log_lines, "System: Hearts are broken.")
            return

        if event_name == "trick_winner":
            append_event_log_line(
                event_log_lines,
                f"System: {payload['winner'].name} takes the trick.",
            )
            return

        if event_name == "hand_complete":
            append_event_log_line(event_log_lines, "System: Hand complete.")
            return

        if event_name == "match_result":
            message_var.set(payload["result"].result_text)
            append_event_log_line(event_log_lines, f"System: {payload['result'].result_text}")

    return on_event


def build_illegal_play_message(state, selected_card, playable_cards: list[Card]) -> str:
    if state.round_number == 1 and not state.current_trick:
        two_of_clubs = Card(suit="clubs", rank="2")
        if two_of_clubs in state.players[0].hand:
            return "Illegal play: you must lead the 2 of clubs."

    if state.current_trick:
        lead_suit = state.current_trick[0].suit
        if any(card.suit == lead_suit for card in state.players[0].hand):
            return f"Illegal play: you must follow {lead_suit}."
        if state.round_number == 1 and (
            selected_card.suit == "hearts" or (selected_card.suit == "spades" and selected_card.rank == "Q")
        ):
            return "Illegal play: avoid point cards on the first trick if you can."

    if selected_card.suit == "hearts" and any(card.suit != "hearts" for card in state.players[0].hand):
        return "Illegal play: hearts cannot be led yet."

    legal_labels = ", ".join(str(card) for card in playable_cards[:3])
    if len(playable_cards) > 3:
        legal_labels += ", ..."
    return f"Illegal play: try {legal_labels}."


def render_event_log(
    alfred_note: str,
    helper_note: str,
    system_note: str,
    event_log_lines: list[str],
    event_log_text: tk.Text,
) -> None:
    latest_lines = list(event_log_lines)
    if not latest_lines or latest_lines[-1] != f"Alfred: {alfred_note}":
        latest_lines.append(f"Alfred: {alfred_note}")
    if latest_lines[-1] != f"Helper: {helper_note}" and f"Helper: {helper_note}" not in latest_lines[-2:]:
        latest_lines.append(f"Helper: {helper_note}")
    if latest_lines[-1] != f"System: {system_note}" and f"System: {system_note}" not in latest_lines[-2:]:
        latest_lines.append(f"System: {system_note}")
    event_log_lines[:] = latest_lines[-14:]

    event_log_text.configure(state="normal")
    event_log_text.delete("1.0", "end")
    event_log_text.insert("1.0", "\n".join(event_log_lines))
    event_log_text.configure(state="disabled")


def request_helper_hint(
    controller: HeartsMatchController,
    alfred_dialogue_var: tk.StringVar,
    dialogue_note_var: tk.StringVar,
    message_var: tk.StringVar,
    current_trick_var: tk.StringVar,
    event_log_lines: list[str],
    event_log_text: tk.Text,
) -> None:
    helper_hint = controller.request_helper_hint()
    state = controller.get_state()
    current_trick_var.set(get_current_trick_display_text(state))
    render_event_log(
        alfred_note=alfred_dialogue_var.get(),
        helper_note=dialogue_note_var.get(),
        system_note=message_var.get(),
        event_log_lines=event_log_lines,
        event_log_text=event_log_text,
    )


def append_event_log_line(event_log_lines: list[str], line: str) -> None:
    if event_log_lines and event_log_lines[-1] == line:
        return
    event_log_lines.append(line)
    del event_log_lines[:-14]

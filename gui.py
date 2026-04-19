from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, END, LEFT, RIGHT, X, Y

from main import DATETIME_FORMAT, Workout, WorkoutService


APP_TITLE = "FitCache"
APP_SIZE = (1440, 920)
APP_MIN_SIZE = (1240, 780)
THEME_NAME = "superhero"
ADD_EXERCISE_OPTION = "Add Exercise..."

BG_COLOR = "#0b1020"
CARD_COLOR = "#172033"
CARD_ALT = "#1d2940"
PRIMARY_COLOR = "#22c7ff"
ACCENT_COLOR = "#f59e0b"
SUCCESS_COLOR = "#22c55e"
TEXT_COLOR = "#f3f7ff"
MUTED_TEXT = "#9fb0cc"
FAINT_TEXT = "#6f84a8"
ENTRY_BG = "#0f1728"

MILESTONES = [
    {"name": "Foundation Tier", "weight": 1000, "icon": "●", "descriptor": "Your training base is taking shape."},
    {"name": "Performance Tier", "weight": 5000, "icon": "◆", "descriptor": "A strong body of work is building across your sessions."},
    {"name": "Piano Tier", "weight": 8000, "icon": "■", "descriptor": "You have moved the equivalent of a grand piano."},
    {"name": "Elephant Tier", "weight": 12000, "icon": "▲", "descriptor": "You have moved the equivalent of an elephant."},
    {"name": "Heavy Transport Tier", "weight": 30000, "icon": "★", "descriptor": "An elite lifetime load milestone has been reached."},
]


class FitCacheApp(ttk.Window):
    def __init__(self, service: WorkoutService | None = None) -> None:
        super().__init__(
            title=APP_TITLE,
            themename=THEME_NAME,
            size=APP_SIZE,
            minsize=APP_MIN_SIZE,
            hdpi=True,
        )

        self.state("zoomed")
        self.service = service or WorkoutService()
        self.configure(bg=BG_COLOR)

        self.selected_workout: Workout | None = None
        self.exercise_names: list[str] = []

        self.status_var = tk.StringVar(value="Welcome to FitCache.")
        self.exercise_var = tk.StringVar()
        self.sets_var = tk.StringVar()
        self.reps_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.datetime_var = tk.StringVar()

        self.total_workouts_var = tk.StringVar(value="0")
        self.total_sets_var = tk.StringVar(value="0")
        self.total_reps_var = tk.StringVar(value="0")
        self.total_duration_var = tk.StringVar(value="0 min")
        self.top_exercise_var = tk.StringVar(value="N/A")
        self.total_volume_var = tk.StringVar(value="0.0 lb")

        self.milestone_title_var = tk.StringVar(value="Starter Load")
        self.milestone_copy_var = tk.StringVar(value="Log your first sessions to unlock milestones.")
        self.milestone_stat_var = tk.StringVar(value="0.0 lb moved")
        self.next_goal_var = tk.StringVar(value="Next milestone: 1,000 lb")
        self.progress_percent_var = tk.StringVar(value="0%")

        self._configure_styles()
        self._build_layout()
        self._set_default_datetime()
        self.refresh_all_views()

    def _configure_styles(self) -> None:
        style = self.style

        self.option_add("*Font", ("Segoe UI", 10))

        style.configure("TFrame", background=BG_COLOR)
        style.configure("App.TFrame", background=BG_COLOR)
        style.configure("Card.TFrame", background=CARD_COLOR)
        style.configure("Alt.TFrame", background=CARD_ALT)

        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI Semibold", 10))

        style.configure(
            "AppTitle.TLabel",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI Semibold", 28),
        )
        style.configure(
            "Subtitle.TLabel",
            background=BG_COLOR,
            foreground=MUTED_TEXT,
            font=("Segoe UI", 11),
        )
        style.configure(
            "Section.TLabel",
            background=CARD_COLOR,
            foreground=TEXT_COLOR,
            font=("Segoe UI Semibold", 12),
        )
        style.configure(
            "SectionAlt.TLabel",
            background=CARD_ALT,
            foreground=TEXT_COLOR,
            font=("Segoe UI Semibold", 12),
        )
        style.configure("Card.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR)
        style.configure("Muted.Card.TLabel", background=CARD_COLOR, foreground=MUTED_TEXT)
        style.configure("Alt.TLabel", background=CARD_ALT, foreground=TEXT_COLOR)
        style.configure("Muted.Alt.TLabel", background=CARD_ALT, foreground=MUTED_TEXT)
        style.configure(
            "MetricTitle.TLabel",
            background=CARD_COLOR,
            foreground=MUTED_TEXT,
            font=("Segoe UI", 9),
        )

        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, style="App.TFrame", padding=18)
        outer.pack(fill=BOTH, expand=True)

        self._build_header(outer)
        self._build_tabs(outer)
        self._build_status_bar()

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="App.TFrame")
        header.pack(fill=X, pady=(0, 12))

        title_wrap = ttk.Frame(header, style="App.TFrame")
        title_wrap.pack(side=LEFT, fill=X, expand=True)

        ttk.Label(
            title_wrap,
            text="FitCache Performance Dashboard",
            style="AppTitle.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            title_wrap,
            text="A workout tracker that makes progress feel powerful, visual, and presentation-ready.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        badge = tk.Label(
            header,
            text="LIVE WORKOUT INTELLIGENCE",
            bg=BG_COLOR,
            fg=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 9),
            padx=10,
            pady=6,
        )
        badge.pack(side=RIGHT, anchor="n")

    def _build_tabs(self, parent: ttk.Frame) -> None:
        self.notebook = ttk.Notebook(parent, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)

        self.dashboard_tab = ttk.Frame(self.notebook, style="App.TFrame", padding=8)
        self.log_tab = ttk.Frame(self.notebook, style="App.TFrame", padding=8)
        self.history_tab = ttk.Frame(self.notebook, style="App.TFrame", padding=8)
        self.summary_tab = ttk.Frame(self.notebook, style="App.TFrame", padding=8)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.log_tab, text="Log Workout")
        self.notebook.add(self.history_tab, text="History")
        self.notebook.add(self.summary_tab, text="Summary")

        self._build_dashboard_tab()
        self._build_log_tab()
        self._build_history_tab()
        self._build_summary_tab()

    def _build_dashboard_tab(self) -> None:
        summary_frame = ttk.Frame(self.dashboard_tab, style="App.TFrame")
        summary_frame.pack(fill=X, pady=(0, 14))

        for index in range(6):
            summary_frame.columnconfigure(index, weight=1)

        self._create_metric_card(summary_frame, "Total Workouts", self.total_workouts_var, 0)
        self._create_metric_card(summary_frame, "Total Sets", self.total_sets_var, 1)
        self._create_metric_card(summary_frame, "Total Reps", self.total_reps_var, 2)
        self._create_metric_card(summary_frame, "Total Duration", self.total_duration_var, 3)
        self._create_metric_card(summary_frame, "Top Exercise", self.top_exercise_var, 4)
        self._create_metric_card(summary_frame, "Total Volume", self.total_volume_var, 5)

        lower = ttk.Frame(self.dashboard_tab, style="App.TFrame")
        lower.pack(fill=BOTH, expand=True)

        left = ttk.Frame(lower, style="App.TFrame")
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        right = ttk.Frame(lower, style="App.TFrame")
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        self._build_recent_history_panel(left)
        self._build_dashboard_insights_panel(right)
        self._build_dashboard_milestone_preview(right)

    def _build_log_tab(self) -> None:
        form_card = ttk.Frame(self.log_tab, style="Card.TFrame", padding=20)
        form_card.pack(fill=X, pady=(4, 12))

        ttk.Label(
            form_card,
            text="Log Workout",
            style="Section.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))

        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(1, weight=1)

        self._create_exercise_dropdown(form_card, 1, 0)
        self._create_entry_field(form_card, "Sets", self.sets_var, 1, 1)
        self._create_entry_field(form_card, "Reps", self.reps_var, 2, 0)
        self._create_entry_field(form_card, "Weight (lb)", self.weight_var, 2, 1)
        self._create_entry_field(form_card, "Duration (minutes)", self.duration_var, 3, 0)
        self._create_entry_field(form_card, "Date & Time", self.datetime_var, 3, 1, readonly=True)

        button_row = ttk.Frame(form_card, style="Card.TFrame")
        button_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(
            button_row,
            text="Save Workout",
            bootstyle="info",
            command=self.save_workout,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_row,
            text="Clear Form",
            bootstyle="secondary",
            command=self.clear_form,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        tips_card = ttk.Frame(self.log_tab, style="Alt.TFrame", padding=18)
        tips_card.pack(fill=X)

        ttk.Label(
            tips_card,
            text="Beginner Tips",
            style="SectionAlt.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        ttk.Label(
            tips_card,
            text="Choose an exercise from the list or use Add Exercise... to create a new one. The service layer will normalize capitalization and common spelling issues when saving.",
            style="Muted.Alt.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w")

    def _build_history_tab(self) -> None:
        history_card = ttk.Frame(self.history_tab, style="Card.TFrame", padding=18)
        history_card.pack(fill=BOTH, expand=True)

        header = ttk.Frame(history_card, style="Card.TFrame")
        header.pack(fill=X, pady=(0, 12))

        ttk.Label(header, text="Workout History", style="Section.TLabel").pack(side=LEFT)

        button_wrap = ttk.Frame(header, style="Card.TFrame")
        button_wrap.pack(side=RIGHT)

        ttk.Button(
            button_wrap,
            text="Refresh",
            bootstyle="secondary-outline",
            command=self.refresh_all_views,
        ).pack(side=LEFT, padx=(0, 8))

        ttk.Button(
            button_wrap,
            text="Delete Selected",
            bootstyle="danger",
            command=self.delete_selected_workout,
        ).pack(side=LEFT)

        table_frame = ttk.Frame(history_card, style="Card.TFrame")
        table_frame.pack(fill=BOTH, expand=True)

        columns = ("exercise", "sets", "reps", "weight", "duration", "date")
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            bootstyle="info",
        )

        headings = {
            "exercise": "Exercise",
            "sets": "Sets",
            "reps": "Reps",
            "weight": "Weight",
            "duration": "Minutes",
            "date": "Date / Time",
        }
        widths = {
            "exercise": 220,
            "sets": 90,
            "reps": 90,
            "weight": 110,
            "duration": 110,
            "date": 180,
        }

        for column in columns:
            self.history_tree.heading(column, text=headings[column])
            self.history_tree.column(column, width=widths[column], anchor="center")

        self.history_tree.column("exercise", anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.history_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_summary_tab(self) -> None:
        top = ttk.Frame(self.summary_tab, style="App.TFrame")
        top.pack(fill=X, pady=(0, 12))

        insights_card = ttk.Frame(top, style="Alt.TFrame", padding=18)
        insights_card.pack(fill=X)

        ttk.Label(
            insights_card,
            text="Insights",
            style="SectionAlt.TLabel",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        insights_card.columnconfigure(0, weight=1)
        insights_card.columnconfigure(1, weight=1)

        self._create_summary_row(insights_card, "Top Exercise", self.top_exercise_var, 1)
        self._create_summary_row(insights_card, "Total Volume", self.total_volume_var, 2)
        self._create_summary_row(insights_card, "Milestone", self.milestone_title_var, 3)

        milestone_card = ttk.Frame(self.summary_tab, style="Card.TFrame", padding=18)
        milestone_card.pack(fill=BOTH, expand=True)

        milestone_card.columnconfigure(0, weight=2)
        milestone_card.columnconfigure(1, weight=3)

        left_visual = tk.Canvas(
            milestone_card,
            width=320,
            height=180,
            bg=CARD_COLOR,
            highlightthickness=0,
            bd=0,
        )
        left_visual.grid(row=0, column=0, sticky="w", padx=(0, 18))

        left_visual.create_rectangle(16, 18, 304, 162, fill=ENTRY_BG, outline="")
        left_visual.create_oval(36, 34, 118, 116, fill="#16314d", outline="")
        left_visual.create_oval(90, 46, 194, 150, fill="#1c486d", outline="")
        left_visual.create_oval(156, 58, 284, 154, fill="#245b88", outline="")
        left_visual.create_text(
            160,
            48,
            text="LIFETIME LOAD",
            fill=MUTED_TEXT,
            font=("Segoe UI Semibold", 12),
        )
        self.visual_icon_text = left_visual.create_text(
            160,
            102,
            text="▲",
            fill=ACCENT_COLOR,
            font=("Segoe UI Symbol", 52, "bold"),
        )
        self.visual_class_text = left_visual.create_text(
            160,
            142,
            text="Starter Load",
            fill=TEXT_COLOR,
            font=("Segoe UI Semibold", 14),
        )
        self.visual_canvas = left_visual

        info = ttk.Frame(milestone_card, style="Card.TFrame")
        info.grid(row=0, column=1, sticky="nsew")
        info.columnconfigure(0, weight=1)

        tk.Label(
            info,
            text="Lifetime Load Moved",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI Semibold", 18),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            info,
            text="A running measure of total strength output across every logged workout.",
            bg=CARD_COLOR,
            fg=MUTED_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 4))

        tk.Label(
            info,
            textvariable=self.milestone_stat_var,
            bg=CARD_COLOR,
            fg=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 28),
        ).grid(row=2, column=0, sticky="w", pady=(6, 4))

        tk.Label(
            info,
            textvariable=self.milestone_copy_var,
            bg=CARD_COLOR,
            fg=MUTED_TEXT,
            justify="left",
            wraplength=620,
            font=("Segoe UI", 11),
        ).grid(row=3, column=0, sticky="w", pady=(0, 14))

        self.progress = ttk.Progressbar(
            info,
            bootstyle="info-striped",
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
        )
        self.progress.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        meta = ttk.Frame(info, style="Card.TFrame")
        meta.grid(row=5, column=0, sticky="ew")
        meta.columnconfigure(0, weight=1)
        meta.columnconfigure(1, weight=0)

        tk.Label(
            meta,
            textvariable=self.next_goal_var,
            bg=CARD_COLOR,
            fg=FAINT_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            meta,
            textvariable=self.progress_percent_var,
            bg=CARD_COLOR,
            fg=ACCENT_COLOR,
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=1, sticky="e")

    def _build_recent_history_panel(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill=BOTH, expand=True)

        ttk.Label(card, text="Recent Workouts", style="Section.TLabel").pack(anchor="w", pady=(0, 12))

        columns = ("exercise", "sets", "reps", "weight", "duration", "date")
        self.dashboard_tree = ttk.Treeview(
            card,
            columns=columns,
            show="headings",
            height=10,
            bootstyle="info",
        )

        headings = {
            "exercise": "Exercise",
            "sets": "Sets",
            "reps": "Reps",
            "weight": "Weight",
            "duration": "Minutes",
            "date": "Date / Time",
        }

        for column, label in headings.items():
            self.dashboard_tree.heading(column, text=label)

        self.dashboard_tree.column("exercise", width=180, anchor="w")
        self.dashboard_tree.column("sets", width=70, anchor="center")
        self.dashboard_tree.column("reps", width=70, anchor="center")
        self.dashboard_tree.column("weight", width=90, anchor="center")
        self.dashboard_tree.column("duration", width=90, anchor="center")
        self.dashboard_tree.column("date", width=160, anchor="center")

        self.dashboard_tree.pack(fill=BOTH, expand=True)

    def _build_dashboard_insights_panel(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Alt.TFrame", padding=18)
        card.pack(fill=X, pady=(0, 10))

        ttk.Label(card, text="Insights", style="SectionAlt.TLabel").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 12),
        )
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        self._create_summary_row(card, "Top Exercise", self.top_exercise_var, 1)
        self._create_summary_row(card, "Total Volume", self.total_volume_var, 2)
        self._create_summary_row(card, "Milestone", self.milestone_title_var, 3)

    def _build_dashboard_milestone_preview(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.pack(fill=BOTH, expand=True)

        ttk.Label(card, text="Milestone Preview", style="Section.TLabel").pack(anchor="w", pady=(0, 12))

        ttk.Label(
            card,
            textvariable=self.milestone_title_var,
            style="Card.TLabel",
            font=("Segoe UI Semibold", 18),
        ).pack(anchor="w")

        ttk.Label(
            card,
            textvariable=self.milestone_stat_var,
            style="Card.TLabel",
            font=("Segoe UI Semibold", 24),
            foreground=PRIMARY_COLOR,
        ).pack(anchor="w", pady=(8, 4))

        ttk.Label(
            card,
            textvariable=self.milestone_copy_var,
            style="Muted.Card.TLabel",
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        self.preview_progress = ttk.Progressbar(
            card,
            bootstyle="warning-striped",
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
        )
        self.preview_progress.pack(fill=X, pady=(0, 8))

        meta = ttk.Frame(card, style="Card.TFrame")
        meta.pack(fill=X)

        ttk.Label(meta, textvariable=self.next_goal_var, style="Muted.Card.TLabel").pack(side=LEFT)
        tk.Label(
            meta,
            textvariable=self.progress_percent_var,
            bg=CARD_COLOR,
            fg=ACCENT_COLOR,
            font=("Segoe UI Semibold", 10),
        ).pack(side=RIGHT)

    def _build_status_bar(self) -> None:
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            anchor="w",
            bg="#10182a",
            fg=SUCCESS_COLOR,
            padx=14,
            pady=10,
            font=("Segoe UI", 10),
        )
        status_bar.pack(fill=X, side="bottom")

    def _create_metric_card(
        self,
        parent: ttk.Frame,
        title: str,
        value_var: tk.StringVar,
        column: int,
    ) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))

        ttk.Label(card, text=title, style="MetricTitle.TLabel").pack(anchor="w")
        tk.Label(
            card,
            textvariable=value_var,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI Semibold", 20),
        ).pack(anchor="w", pady=(8, 0))

    def _create_exercise_dropdown(self, parent: ttk.Frame, row: int, column: int) -> None:
        ttk.Label(parent, text="Exercise Name", style="Card.TLabel").grid(
            row=row * 2 - 1,
            column=column,
            sticky="w",
            padx=(0, 8),
            pady=(4, 4),
        )

        self.exercise_combobox = ttk.Combobox(
            parent,
            textvariable=self.exercise_var,
            state="readonly",
            bootstyle="info",
        )
        self.exercise_combobox.grid(
            row=row * 2,
            column=column,
            sticky="ew",
            padx=(0, 8),
            pady=(0, 8),
        )
        self.exercise_combobox.bind("<<ComboboxSelected>>", self._on_exercise_selected)

    def _create_entry_field(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        row: int,
        column: int,
        readonly: bool = False,
    ) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(
            row=row * 2 - 1,
            column=column,
            sticky="w",
            padx=(0, 8),
            pady=(4, 4),
        )

        entry = ttk.Entry(parent, textvariable=variable)
        if readonly:
            entry.configure(state="readonly")

        entry.grid(row=row * 2, column=column, sticky="ew", padx=(0, 8), pady=(0, 8))

    def _create_summary_row(
        self,
        parent: ttk.Frame,
        label: str,
        value_var: tk.StringVar,
        row: int,
    ) -> None:
        tk.Label(
            parent,
            text=label,
            bg=CARD_ALT,
            fg=MUTED_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=row, column=0, sticky="w", pady=6)

        tk.Label(
            parent,
            textvariable=value_var,
            bg=CARD_ALT,
            fg=TEXT_COLOR,
            font=("Segoe UI Semibold", 10),
        ).grid(row=row, column=1, sticky="e", pady=6)

    def _set_default_datetime(self) -> None:
        self.datetime_var.set(datetime.now().strftime(DATETIME_FORMAT))

    def _refresh_exercise_dropdown(self) -> None:
        self.exercise_names = self.service.get_all_exercise_names()
        values = [*self.exercise_names, ADD_EXERCISE_OPTION]
        self.exercise_combobox["values"] = values

        current_value = self.exercise_var.get()
        if current_value in self.exercise_names:
            return

        if self.exercise_names:
            self.exercise_var.set(self.exercise_names[0])
        else:
            self.exercise_var.set("")

    def _on_exercise_selected(self, _event: tk.Event) -> None:
        if self.exercise_var.get() != ADD_EXERCISE_OPTION:
            return

        entered_name = simpledialog.askstring(
            "Add Exercise",
            "Enter a new exercise name:",
            parent=self,
        )

        if entered_name is None:
            if self.exercise_names:
                self.exercise_var.set(self.exercise_names[0])
            else:
                self.exercise_var.set("")
            return

        normalized_name = self.service.normalize_exercise_name(entered_name)
        if not normalized_name:
            messagebox.showwarning("Invalid Exercise", "Exercise name cannot be empty.")
            if self.exercise_names:
                self.exercise_var.set(self.exercise_names[0])
            else:
                self.exercise_var.set("")
            return

        if normalized_name not in self.exercise_names:
            self.exercise_names.append(normalized_name)
            self.exercise_names.sort()
            self.exercise_combobox["values"] = [*self.exercise_names, ADD_EXERCISE_OPTION]

        self.exercise_var.set(normalized_name)
        self.status_var.set(f"Ready to save new exercise: {normalized_name}")

    def clear_form(self) -> None:
        self.sets_var.set("")
        self.reps_var.set("")
        self.weight_var.set("")
        self.duration_var.set("")
        self._set_default_datetime()

        if self.exercise_names:
            self.exercise_var.set(self.exercise_names[0])
        else:
            self.exercise_var.set("")

        self.status_var.set("Form cleared.")

    def save_workout(self) -> None:
        try:
            workout = self.service.add_workout(
                exercise_name=self.exercise_var.get(),
                sets=int(self.sets_var.get()),
                reps=int(self.reps_var.get()),
                weight=float(self.weight_var.get()),
                duration=int(self.duration_var.get()),
                workout_datetime=self.datetime_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_var.set("Unable to save workout. Please correct the form.")
            return
        except Exception as exc:
            messagebox.showerror("Application Error", f"An unexpected error occurred:\n\n{exc}")
            self.status_var.set("An unexpected error occurred.")
            return

        self.refresh_all_views()
        self.clear_form()
        self.status_var.set(f"Saved workout: {workout.exercise_name}.")
        messagebox.showinfo("Success", "Workout saved successfully.")

    def delete_selected_workout(self) -> None:
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a workout to delete.")
            self.status_var.set("No workout selected for deletion.")
            return

        item_id = selected[0]
        tags = self.history_tree.item(item_id, "tags")
        workout_tag = tags[0] if tags else None

        if workout_tag is None:
            messagebox.showerror("Error", "Could not identify the selected workout.")
            self.status_var.set("Delete failed: missing workout reference.")
            return

        values = self.history_tree.item(item_id, "values")
        exercise_name = values[0]

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete workout '{exercise_name}'?",
        )
        if not confirmed:
            self.status_var.set("Delete cancelled.")
            return

        resolved_workout = self._workout_from_tag(workout_tag)
        if resolved_workout is None:
            messagebox.showerror("Error", "Could not match the selected workout in storage.")
            self.status_var.set("Delete failed: workout not found.")
            return

        deleted = self.service.delete_workout(resolved_workout)
        if deleted:
            self.refresh_all_views()
            self.status_var.set(f"Deleted workout: {resolved_workout.exercise_name}.")
            messagebox.showinfo("Deleted", "Workout deleted successfully.")
        else:
            messagebox.showerror("Delete Failed", "The selected workout could not be deleted.")
            self.status_var.set("Delete failed.")

    def _workout_to_tag(self, workout: Workout) -> str:
        return "|||".join(
            [
                workout.exercise_name,
                str(workout.sets),
                str(workout.reps),
                f"{workout.weight:.1f}",
                str(workout.duration),
                workout.workout_datetime,
            ]
        )

    def _workout_from_tag(self, tag_value: str) -> Workout | None:
        for workout in self.service.get_workouts():
            if self._workout_to_tag(workout) == tag_value:
                return workout
        return None

    def refresh_all_views(self) -> None:
        self._set_default_datetime()

        summary = self.service.get_workout_summary()
        workouts = self.service.get_workouts()

        self.total_workouts_var.set(str(summary["total_workouts"]))
        self.total_sets_var.set(str(summary["total_sets"]))
        self.total_reps_var.set(str(summary["total_reps"]))
        self.total_duration_var.set(f"{summary['total_duration']} min")
        self.top_exercise_var.set(str(summary["top_exercise"]))
        self.total_volume_var.set(f"{summary['total_volume']:.1f} lb")

        self._refresh_tree(self.history_tree, workouts)
        self._refresh_tree(self.dashboard_tree, workouts[:10])
        self._refresh_exercise_dropdown()
        self._update_milestone(float(summary["total_volume"]))

    def _refresh_tree(self, tree: ttk.Treeview, workouts: list[Workout]) -> None:
        for item in tree.get_children():
            tree.delete(item)

        for workout in workouts:
            tree.insert(
                "",
                END,
                values=(
                    workout.exercise_name,
                    workout.sets,
                    workout.reps,
                    f"{workout.weight:.1f}",
                    workout.duration,
                    workout.workout_datetime,
                ),
                tags=(self._workout_to_tag(workout),),
            )

    def _on_tree_select(self, _event: tk.Event) -> None:
        selected = self.history_tree.selection()
        if not selected:
            self.selected_workout = None
            return

        tag_list = self.history_tree.item(selected[0], "tags")
        if not tag_list:
            self.selected_workout = None
            return

        self.selected_workout = self._workout_from_tag(tag_list[0])

    def _update_milestone(self, total_volume: float) -> None:
        current = MILESTONES[0]
        next_target = MILESTONES[0]

        for milestone in MILESTONES:
            if total_volume >= milestone["weight"]:
                current = milestone
            if total_volume < milestone["weight"]:
                next_target = milestone
                break
        else:
            next_target = MILESTONES[-1]

        self.milestone_title_var.set(current["name"])
        self.milestone_stat_var.set(f"{total_volume:,.1f} lb moved")

        if total_volume >= MILESTONES[-1]["weight"]:
            self.milestone_copy_var.set(
                f"You have reached {current['name']}. {current['descriptor']}"
            )
            self.next_goal_var.set("Top milestone reached")
            progress_value = 100
        else:
            lower_bound = 0
            for milestone in MILESTONES:
                if milestone["weight"] == current["weight"]:
                    break
                lower_bound = milestone["weight"]

            span = max(next_target["weight"] - lower_bound, 1)
            progress_value = ((total_volume - lower_bound) / span) * 100
            progress_value = max(0, min(progress_value, 100))

            self.milestone_copy_var.set(
                f"Current milestone: {current['name']}. {current['descriptor']}"
            )
            self.next_goal_var.set(
                f"Next milestone: {next_target['name']} at {next_target['weight']:,} lb moved"
            )

        self.progress["value"] = progress_value
        self.preview_progress["value"] = progress_value
        self.progress_percent_var.set(f"{progress_value:.0f}%")
        self.visual_canvas.itemconfigure(self.visual_icon_text, text=current["icon"])
        self.visual_canvas.itemconfigure(self.visual_class_text, text=current["name"])


def main() -> None:
    app = FitCacheApp()
    app.mainloop()


if __name__ == "__main__":
    main()
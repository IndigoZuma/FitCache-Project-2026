from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from main import DATETIME_FORMAT, WorkoutService


APP_TITLE = "FitCache"
APP_GEOMETRY = "1260x820"

BG_COLOR = "#0b1020"
SURFACE_COLOR = "#121a2b"
CARD_COLOR = "#172033"
CARD_ALT = "#1d2940"
PRIMARY_COLOR = "#22c7ff"
PRIMARY_HOVER = "#14b8f0"
SECONDARY_COLOR = "#7c3aed"
ACCENT_COLOR = "#f59e0b"
SUCCESS_COLOR = "#22c55e"
DANGER_COLOR = "#ef4444"

TEXT_COLOR = "#f3f7ff"
MUTED_TEXT = "#9fb0cc"
FAINT_TEXT = "#6f84a8"
BORDER_COLOR = "#2b3a55"
TABLE_ROW = "#132038"
TABLE_SELECTED = "#23406b"
ENTRY_BG = "#0f1728"

MILESTONES = [
    {"name": "Starter Load", "weight": 1000, "icon": "●", "descriptor": "A strong beginning."},
    {"name": "Motorcycle Class", "weight": 5000, "icon": "◆", "descriptor": "The equivalent of moving a motorcycle."},
    {"name": "Grand Piano Class", "weight": 8000, "icon": "■", "descriptor": "The equivalent of moving a grand piano."},
    {"name": "Elephant Class", "weight": 12000, "icon": "▲", "descriptor": "The equivalent of moving an elephant."},
    {"name": "Truck Class", "weight": 30000, "icon": "★", "descriptor": "A truly elite amount of load moved."},
]


class FitCacheApp(tk.Tk):
    def __init__(self, service: WorkoutService | None = None) -> None:
        super().__init__()
        self.service = service or WorkoutService()

        self.title(APP_TITLE)
        self.geometry("1440x920")
        self.state("zoomed")
        self.minsize(1320, 860)
        self.configure(bg=BG_COLOR)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

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
        self.milestone_stat_var = tk.StringVar(value="0 lb moved")
        self.next_goal_var = tk.StringVar(value="Next milestone: 1,000 lb")
        self.progress_percent_var = tk.StringVar(value="0%")

        self._build_layout()
        self._set_default_datetime()
        self.refresh_dashboard()

    def _configure_styles(self) -> None:
        default_font = ("Segoe UI", 10)
        small_font = ("Segoe UI", 9)
        section_font = ("Segoe UI Semibold", 12)
        heading_font = ("Segoe UI Semibold", 28)
        metric_font = ("Segoe UI Semibold", 22)

        self.option_add("*Font", default_font)

        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Surface.TFrame", background=SURFACE_COLOR)
        self.style.configure("Card.TFrame", background=CARD_COLOR)
        self.style.configure("CardAlt.TFrame", background=CARD_ALT)

        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Card.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Muted.Card.TLabel", background=CARD_COLOR, foreground=MUTED_TEXT)
        self.style.configure("Alt.Card.TLabel", background=CARD_ALT, foreground=TEXT_COLOR)
        self.style.configure("Muted.Alt.Card.TLabel", background=CARD_ALT, foreground=MUTED_TEXT)
        self.style.configure("Hero.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=heading_font)
        self.style.configure("Subhero.TLabel", background=BG_COLOR, foreground=MUTED_TEXT, font=("Segoe UI", 11))
        self.style.configure("Section.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=section_font)
        self.style.configure("MetricTitle.TLabel", background=CARD_COLOR, foreground=MUTED_TEXT, font=small_font)
        self.style.configure("InsightKey.TLabel", background=CARD_COLOR, foreground=MUTED_TEXT, font=small_font)

        self.style.configure(
            "Primary.TButton",
            background=PRIMARY_COLOR,
            foreground="#08101f",
            padding=(14, 10),
            relief="flat",
            borderwidth=0,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", PRIMARY_HOVER), ("pressed", PRIMARY_HOVER)],
        )

        self.style.configure(
            "Secondary.TButton",
            background=CARD_ALT,
            foreground=TEXT_COLOR,
            padding=(14, 10),
            relief="flat",
            borderwidth=0,
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#293a59"), ("pressed", "#293a59")],
        )

        self.style.configure(
            "TEntry",
            fieldbackground=ENTRY_BG,
            foreground=TEXT_COLOR,
            bordercolor=BORDER_COLOR,
            lightcolor=BORDER_COLOR,
            darkcolor=BORDER_COLOR,
            insertcolor=TEXT_COLOR,
            padding=8,
        )

        self.style.configure(
            "Treeview",
            background=TABLE_ROW,
            fieldbackground=TABLE_ROW,
            foreground=TEXT_COLOR,
            bordercolor=BORDER_COLOR,
            lightcolor=BORDER_COLOR,
            darkcolor=BORDER_COLOR,
            rowheight=32,
        )
        self.style.map(
            "Treeview",
            background=[("selected", TABLE_SELECTED)],
            foreground=[("selected", TEXT_COLOR)],
        )
        self.style.configure(
            "Treeview.Heading",
            background=CARD_ALT,
            foreground=TEXT_COLOR,
            bordercolor=BORDER_COLOR,
            lightcolor=CARD_ALT,
            darkcolor=CARD_ALT,
            font=("Segoe UI Semibold", 10),
            relief="flat",
            padding=(8, 8),
        )

        self.style.configure(
            "Volume.Horizontal.TProgressbar",
            troughcolor="#0e1627",
            bordercolor="#0e1627",
            background=PRIMARY_COLOR,
            lightcolor=PRIMARY_COLOR,
            darkcolor=PRIMARY_COLOR,
            thickness=18,
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=20, style="TFrame")
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="FitCache Performance Dashboard", style="Hero.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="A workout tracker that makes progress feel powerful, visual, and presentation-ready.",
            style="Subhero.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        hero_badge = tk.Label(
            header,
            text="LIVE WORKOUT INTELLIGENCE",
            bg=BG_COLOR,
            fg=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 9),
            padx=10,
            pady=4,
        )
        hero_badge.grid(row=0, column=1, sticky="e")

        summary_frame = ttk.Frame(container, style="TFrame")
        summary_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        for index in range(6):
            summary_frame.columnconfigure(index, weight=1)

        self._create_metric_card(summary_frame, "Total Workouts", self.total_workouts_var, 0)
        self._create_metric_card(summary_frame, "Total Sets", self.total_sets_var, 1)
        self._create_metric_card(summary_frame, "Total Reps", self.total_reps_var, 2)
        self._create_metric_card(summary_frame, "Total Duration", self.total_duration_var, 3)
        self._create_metric_card(summary_frame, "Top Exercise", self.top_exercise_var, 4)
        self._create_metric_card(summary_frame, "Total Volume", self.total_volume_var, 5)

        main_panel = ttk.Frame(container, style="TFrame")
        main_panel.grid(row=2, column=0, sticky="nsew")
        main_panel.rowconfigure(0, weight=1)
        main_panel.rowconfigure(1, weight=0)
        main_panel.rowconfigure(2, weight=0)
        main_panel.rowconfigure(0, weight=1)
        main_panel.rowconfigure(1, weight=0)

        history_card = ttk.Frame(main_panel, style="Card.TFrame", padding=16)
        history_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        history_card.columnconfigure(0, weight=1)
        history_card.rowconfigure(1, weight=1)

        ttk.Label(history_card, text="Workout History", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))

        columns = ("exercise", "sets", "reps", "weight", "duration", "date")
        self.history_tree = ttk.Treeview(history_card, columns=columns, show="headings")
        headings = {
            "exercise": "Exercise",
            "sets": "Sets",
            "reps": "Reps",
            "weight": "Weight",
            "duration": "Minutes",
            "date": "Date / Time",
        }
        widths = {
            "exercise": 160,
            "sets": 70,
            "reps": 70,
            "weight": 90,
            "duration": 90,
            "date": 160,
        }

        for column in columns:
            self.history_tree.heading(column, text=headings[column])
            self.history_tree.column(column, width=widths[column], anchor="center")

        scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        right_panel = ttk.Frame(main_panel, style="TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=3)
        right_panel.rowconfigure(1, weight=2)

        form_card = ttk.Frame(right_panel, style="Card.TFrame", padding=16)
        form_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(1, weight=1)

        ttk.Label(form_card, text="Log Workout", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        self._create_field(form_card, "Exercise Name", self.exercise_var, 1, 0)
        self._create_field(form_card, "Sets", self.sets_var, 1, 1)
        self._create_field(form_card, "Reps", self.reps_var, 2, 0)
        self._create_field(form_card, "Weight (lb)", self.weight_var, 2, 1)
        self._create_field(form_card, "Duration (minutes)", self.duration_var, 3, 0)
        self._create_field(form_card, f"Date & Time ({DATETIME_FORMAT})", self.datetime_var, 3, 1)

        button_row = ttk.Frame(form_card, style="Card.TFrame")
        button_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(button_row, text="Save Workout", style="Primary.TButton", command=self.save_workout).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(button_row, text="Clear Form", style="Secondary.TButton", command=self.clear_form).grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        insights_card = ttk.Frame(right_panel, style="CardAlt.TFrame", padding=16)
        insights_card.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        insights_card.columnconfigure(0, weight=1)
        insights_card.columnconfigure(1, weight=1)

        insights_card = ttk.Frame(main_panel, style="CardAlt.TFrame", padding=16)
        insights_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        insights_card.columnconfigure(0, weight=1)
        insights_card.columnconfigure(1, weight=1)
        insights_card.columnconfigure(2, weight=1)

        tk.Label(
        insights_card,
        text="Insights",
        bg=CARD_ALT,
        fg=TEXT_COLOR,
        font=("Segoe UI Semibold", 12),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        self._create_insight_row(insights_card, "Top Exercise", self.top_exercise_var, 1)
        self._create_insight_row(insights_card, "Total Volume", self.total_volume_var, 2)
        self._create_insight_row(insights_card, "Milestone", self.milestone_title_var, 3)

        milestone_card = ttk.Frame(main_panel, style="Card.TFrame", padding=18)
        milestone_card.grid(row=2, column=0, columnspan=2, sticky="ew")

        
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

        left_visual.create_rectangle(16, 18, 304, 162, fill="#0f1728", outline="")
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

        milestone_info = ttk.Frame(milestone_card, style="Card.TFrame")
        milestone_info.grid(row=0, column=1, sticky="nsew")
        milestone_info.columnconfigure(0, weight=1)

        tk.Label(
            milestone_info,
            text="Lifetime Load Moved",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI Semibold", 18),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            milestone_info,
            textvariable=self.milestone_stat_var,
            bg=CARD_COLOR,
            fg=PRIMARY_COLOR,
            font=("Segoe UI Semibold", 28),
        ).grid(row=1, column=0, sticky="w", pady=(4, 2))

        tk.Label(
            milestone_info,
            textvariable=self.milestone_copy_var,
            bg=CARD_COLOR,
            fg=MUTED_TEXT,
            justify="left",
            wraplength=560,
            font=("Segoe UI", 11),
        ).grid(row=2, column=0, sticky="w", pady=(0, 14))

        self.progress = ttk.Progressbar(
            milestone_info,
            style="Volume.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0,
        )
        self.progress.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        progress_meta = ttk.Frame(milestone_info, style="Card.TFrame")
        progress_meta.grid(row=4, column=0, sticky="ew")
        progress_meta.columnconfigure(0, weight=1)
        progress_meta.columnconfigure(1, weight=0)

        tk.Label(
            progress_meta,
            textvariable=self.next_goal_var,
            bg=CARD_COLOR,
            fg=FAINT_TEXT,
            font=("Segoe UI", 10),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            progress_meta,
            textvariable=self.progress_percent_var,
            bg=CARD_COLOR,
            fg=ACCENT_COLOR,
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=1, sticky="e")

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
        status_bar.pack(fill="x", side="bottom")

    def _create_metric_card(self, parent: ttk.Frame, title: str, value_var: tk.StringVar, column: int) -> None:
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

    def _create_field(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(
            row=row * 2 - 1,
            column=column,
            sticky="w",
            padx=(0, 8),
            pady=(4, 4),
        )
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row * 2, column=column, sticky="ew", padx=(0, 8), pady=(0, 8))

    def _create_insight_row(self, parent: ttk.Frame, label: str, value_var: tk.StringVar, row: int) -> None:
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
        self.datetime_var.set(__import__("datetime").datetime.now().strftime(DATETIME_FORMAT))

    def clear_form(self) -> None:
        self.exercise_var.set("")
        self.sets_var.set("")
        self.reps_var.set("")
        self.weight_var.set("")
        self.duration_var.set("")
        self._set_default_datetime()
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
            messagebox.showerror("Application Error", f"An unexpected error occurred: {exc}")
            self.status_var.set("An unexpected error occurred.")
            return

        self.refresh_dashboard()
        self.clear_form()
        self.status_var.set(f"Saved workout: {workout.exercise_name}.")
        messagebox.showinfo("Success", "Workout saved successfully.")

    def refresh_dashboard(self) -> None:
        summary = self.service.get_workout_summary()
        workouts = self.service.get_workouts()

        self.total_workouts_var.set(str(summary["total_workouts"]))
        self.total_sets_var.set(str(summary["total_sets"]))
        self.total_reps_var.set(str(summary["total_reps"]))
        self.total_duration_var.set(f"{summary['total_duration']} min")
        self.top_exercise_var.set(str(summary["top_exercise"]))
        self.total_volume_var.set(f"{summary['total_volume']:.1f} lb")

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        for workout in workouts:
            self.history_tree.insert(
                "",
                "end",
                values=(
                    workout.exercise_name,
                    workout.sets,
                    workout.reps,
                    f"{workout.weight:.1f}",
                    workout.duration,
                    workout.workout_datetime,
                ),
            )

        self._update_milestone(summary["total_volume"])

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
                f"You are currently in {current['name']}. {current['descriptor']}"
            )
            self.next_goal_var.set(f"Next milestone: {next_target['name']} at {next_target['weight']:,} lb")

        self.progress["value"] = progress_value
        self.progress_percent_var.set(f"{progress_value:.0f}%")
        self.visual_canvas.itemconfigure(self.visual_icon_text, text=current["icon"])
        self.visual_canvas.itemconfigure(self.visual_class_text, text=current["name"])

    def mainloop_safe(self) -> None:
        self.mainloop()


def main() -> None:
    app = FitCacheApp()
    app.mainloop_safe()


if __name__ == "__main__":
    main()
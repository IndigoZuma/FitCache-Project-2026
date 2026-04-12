from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from main import DATETIME_FORMAT, WorkoutService

APP_TITLE = "FitCache"
APP_GEOMETRY = "1000x680"
PRIMARY_COLOR = "#2563eb"
BG_COLOR = "#f4f7fb"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#1f2937"
MUTED_TEXT = "#6b7280"
SUCCESS_COLOR = "#166534"
BORDER_COLOR = "#dbe3ef"


class FitCacheApp(tk.Tk):
    def __init__(self, service: WorkoutService | None = None) -> None:
        super().__init__()
        self.service = service or WorkoutService()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(960, 640)
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
        self.total_volume_var = tk.StringVar(value="0")

        self._build_layout()
        self._set_default_datetime()
        self.refresh_dashboard()

    def _configure_styles(self) -> None:
        default_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 11, "bold")

        self.option_add("*Font", default_font)

        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Card.TFrame", background=CARD_COLOR, relief="flat")
        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Card.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Muted.TLabel", background=CARD_COLOR, foreground=MUTED_TEXT)
        self.style.configure("Heading.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 22, "bold"))
        self.style.configure("Section.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=heading_font)
        self.style.configure("Primary.TButton", padding=(14, 8), background=PRIMARY_COLOR, foreground="white")
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8")],
            foreground=[("disabled", "#d1d5db")],
        )
        self.style.configure("Secondary.TButton", padding=(14, 8))
        self.style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=TEXT_COLOR,
            rowheight=28,
            bordercolor=BORDER_COLOR,
            borderwidth=1,
        )
        self.style.configure("Treeview.Heading", font=heading_font)

    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=3)
        container.columnconfigure(1, weight=2)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text=APP_TITLE, style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Professional workout tracking dashboard",
            foreground=MUTED_TEXT,
            background=BG_COLOR,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        summary_frame = ttk.Frame(container)
        summary_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for index in range(4):
            summary_frame.columnconfigure(index, weight=1)

        self._create_metric_card(summary_frame, "Total Workouts", self.total_workouts_var, 0)
        self._create_metric_card(summary_frame, "Total Sets", self.total_sets_var, 1)
        self._create_metric_card(summary_frame, "Total Reps", self.total_reps_var, 2)
        self._create_metric_card(summary_frame, "Total Duration", self.total_duration_var, 3)

        history_card = ttk.Frame(container, style="Card.TFrame", padding=16)
        history_card.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
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
            "date": "Date/Time",
        }
        widths = {
            "exercise": 150,
            "sets": 60,
            "reps": 60,
            "weight": 80,
            "duration": 80,
            "date": 140,
        }
        for column in columns:
            self.history_tree.heading(column, text=headings[column])
            self.history_tree.column(column, width=widths[column], anchor="center")

        scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        right_panel = ttk.Frame(container)
        right_panel.grid(row=2, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=3)
        right_panel.rowconfigure(1, weight=2)
        right_panel.columnconfigure(0, weight=1)

        form_card = ttk.Frame(right_panel, style="Card.TFrame", padding=16)
        form_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        for index in range(2):
            form_card.columnconfigure(index, weight=1)

        ttk.Label(form_card, text="Log Workout", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self._create_field(form_card, "Exercise Name", self.exercise_var, 1, 0)
        self._create_field(form_card, "Sets", self.sets_var, 1, 1)
        self._create_field(form_card, "Reps", self.reps_var, 2, 0)
        self._create_field(form_card, "Weight", self.weight_var, 2, 1)
        self._create_field(form_card, "Duration (minutes)", self.duration_var, 3, 0)
        self._create_field(form_card, f"Date & Time ({DATETIME_FORMAT})", self.datetime_var, 3, 1)

        button_row = ttk.Frame(form_card, style="Card.TFrame")
        button_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        button_row.columnconfigure(0, weight=1)
        button_row.columnconfigure(1, weight=1)

        ttk.Button(button_row, text="Save Workout", style="Primary.TButton", command=self.save_workout).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(button_row, text="Clear Form", style="Secondary.TButton", command=self.clear_form).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        insights_card = ttk.Frame(right_panel, style="Card.TFrame", padding=16)
        insights_card.grid(row=1, column=0, sticky="nsew")
        insights_card.columnconfigure(1, weight=1)

        ttk.Label(insights_card, text="Insights", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        self._create_insight_row(insights_card, "Top Exercise", self.top_exercise_var, 1)
        self._create_insight_row(insights_card, "Total Volume", self.total_volume_var, 2)

        status_bar = tk.Label(self, textvariable=self.status_var, anchor="w", bg="#e8eef9", fg=SUCCESS_COLOR, padx=12, pady=8)
        status_bar.pack(fill="x", side="bottom")

    def _create_metric_card(self, parent: ttk.Frame, title: str, value_var: tk.StringVar, column: int) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        ttk.Label(card, text=title, style="Muted.TLabel").pack(anchor="w")
        tk.Label(card, textvariable=value_var, bg=CARD_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(8, 0))

    def _create_field(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int, column: int) -> None:
        ttk.Label(parent, text=label, style="Card.TLabel").grid(row=row * 2 - 1, column=column, sticky="w", padx=(0, 8), pady=(4, 4))
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row * 2, column=column, sticky="ew", padx=(0, 8), pady=(0, 8))

    def _create_insight_row(self, parent: ttk.Frame, label: str, value_var: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label, style="Muted.TLabel").grid(row=row, column=0, sticky="w", pady=6)
        ttk.Label(parent, textvariable=value_var, style="Card.TLabel").grid(row=row, column=1, sticky="e", pady=6)

    def _set_default_datetime(self) -> None:
        from datetime import datetime
        self.datetime_var.set(datetime.now().strftime(DATETIME_FORMAT))

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


def main() -> None:
    app = FitCacheApp()
    app.mainloop()


if __name__ == "__main__":
    main()
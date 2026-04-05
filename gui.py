import tkinter as tk
from tkinter import messagebox
from main import get_workout_summary


def show_summary():
    summary = get_workout_summary()
    messagebox.showinfo(
        "Workout Summary",
        f"Total workouts: {summary['total_workouts']}\n"
        f"Total sets: {summary['total_sets']}\n"
        f"Total reps: {summary['total_reps']}\n"
        f"Total duration: {summary['total_duration']} minutes"
    )


root = tk.Tk()
root.title("FitCache")
root.geometry("500x400")

title_label = tk.Label(root, text="FitCache", font=("Arial", 20, "bold"))
title_label.pack(pady=20)

subtitle_label = tk.Label(root, text="Personal Fitness Tracker", font=("Arial", 12))
subtitle_label.pack(pady=5)

log_button = tk.Button(root, text="Log Workout", width=20, height=2)
log_button.pack(pady=10)

summary_button = tk.Button(root, text="View Summary", width=20, height=2, command=show_summary)
summary_button.pack(pady=10)

history_button = tk.Button(root, text="View Workout History", width=20, height=2)
history_button.pack(pady=10)

root.mainloop()
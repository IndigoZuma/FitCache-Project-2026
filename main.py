from dataclasses import dataclass, asdict
from datetime import datetime
import json


DATA_FILE = "workouts.json"


@dataclass
class Workout:
    exercise_name: str
    sets: int
    reps: int
    weight: float
    duration: int
    workout_datetime: str

    def to_dict(self) -> dict:
        return asdict(self)


def create_sample_workout() -> Workout:
    return Workout(
        exercise_name="Push Ups",
        sets=3,
        reps=12,
        weight=0.0,
        duration=10,
        workout_datetime=datetime.now().isoformat(timespec="minutes")
    )


def save_workout(workout: Workout) -> None:
    workouts = []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            workouts = json.load(file)
    except FileNotFoundError:
        workouts = []

    workouts.append(workout.to_dict())

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(workouts, file, indent=4)


def load_and_print_workouts() -> None:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            workouts = json.load(file)

        print(f"Loaded {len(workouts)} workouts:")
        for workout in workouts:
            print(
                f"  - {workout['exercise_name']}: "
                f"{workout['sets']}x{workout['reps']} @ "
                f"{workout['weight']}kg, {workout['duration']}min"
            )
    except FileNotFoundError:
        print("No workouts file found yet.")


def print_workout_summary() -> None:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            workouts = json.load(file)

        total_workouts = len(workouts)
        total_sets = sum(workout["sets"] for workout in workouts)
        total_reps = sum(workout["reps"] for workout in workouts)
        total_duration = sum(workout["duration"] for workout in workouts)

        print("\nWorkout Summary:")
        print(f"Total workouts: {total_workouts}")
        print(f"Total sets: {total_sets}")
        print(f"Total reps: {total_reps}")
        print(f"Total duration: {total_duration} minutes")

    except FileNotFoundError:
        print("No workouts file found yet.")
if __name__ == "__main__":
    sample_workout = create_sample_workout()
    save_workout(sample_workout)
    load_and_print_workouts()
    print_workout_summary()  
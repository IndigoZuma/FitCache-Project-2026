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


if __name__ == "__main__":
    workout = create_sample_workout()
    save_workout(workout)
    print("Workout saved to workouts.json")
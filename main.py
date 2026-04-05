import json

DATA_FILE = "workouts.json"


class Workout:
    def __init__(
        self,
        exercise_name: str,
        sets: int,
        reps: int,
        weight: float,
        duration: int,
        workout_datetime: str
    ):
        self.exercise_name = exercise_name
        self.sets = sets
        self.reps = reps
        self.weight = weight
        self.duration = duration
        self.workout_datetime = workout_datetime

    def to_dict(self) -> dict:
        return {
            "exercise_name": self.exercise_name,
            "sets": self.sets,
            "reps": self.reps,
            "weight": self.weight,
            "duration": self.duration,
            "workout_datetime": self.workout_datetime
        }


def save_workout(workout: Workout) -> None:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            workouts = json.load(file)
    except FileNotFoundError:
        workouts = []

    workouts.append(workout.to_dict())

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(workouts, file, indent=4)


def load_workouts() -> list:
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def get_workout_summary() -> dict:
    workouts = load_workouts()

    return {
        "total_workouts": len(workouts),
        "total_sets": sum(workout["sets"] for workout in workouts),
        "total_reps": sum(workout["reps"] for workout in workouts),
        "total_duration": sum(workout["duration"] for workout in workouts)
    }


def print_workout_summary() -> None:
    summary = get_workout_summary()

    print("\nWorkout Summary:")
    print(f"Total workouts: {summary['total_workouts']}")
    print(f"Total sets: {summary['total_sets']}")
    print(f"Total reps: {summary['total_reps']}")
    print(f"Total duration: {summary['total_duration']} minutes")


if __name__ == "__main__":
    workout1 = Workout("Push-ups", 3, 15, 0.0, 10, "2026-04-05T12:30")
    save_workout(workout1)

    workout2 = Workout("Squats", 4, 12, 25.0, 15, "2026-04-05T13:00")
    save_workout(workout2)

    print("Workout history:")
    for workout in load_workouts():
        print(workout)

    print_workout_summary()
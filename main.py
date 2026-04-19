from __future__ import annotations

import json
import string
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from spellchecker import SpellChecker


DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATA_FILE = Path(__file__).with_name("workouts.json")


@dataclass(frozen=True)
class Workout:
    exercise_name: str
    sets: int
    reps: int
    weight: float
    duration: int
    workout_datetime: str


class WorkoutRepository:
    def __init__(self, file_path: Path | str = DATA_FILE) -> None:
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def load_workouts(self) -> list[Workout]:
        try:
            raw_text = self.file_path.read_text(encoding="utf-8").strip()
            if not raw_text:
                return []

            data = json.loads(raw_text)
            if not isinstance(data, list):
                return []

            workouts: list[Workout] = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                workout_datetime = str(
                    item.get(
                        "workout_datetime",
                        datetime.now().strftime(DATETIME_FORMAT),
                    )
                )

                workouts.append(
                    Workout(
                        exercise_name=str(item.get("exercise_name", "")).strip(),
                        sets=int(item.get("sets", 0)),
                        reps=int(item.get("reps", 0)),
                        weight=float(item.get("weight", 0)),
                        duration=int(item.get("duration", 0)),
                        workout_datetime=workout_datetime,
                    )
                )
            return workouts
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return []

    def save_workouts(self, workouts: list[Workout]) -> None:
        data = [asdict(workout) for workout in workouts]
        self.file_path.write_text(json.dumps(data, indent=4), encoding="utf-8")


class WorkoutService:
    def __init__(self, repository: WorkoutRepository | None = None) -> None:
        self.repository = repository or WorkoutRepository()
        self.spell = SpellChecker()

        self.exercise_dictionary_words = {
            "abductor",
            "adductor",
            "bench",
            "bicep",
            "calf",
            "chest",
            "core",
            "curl",
            "deadlift",
            "dip",
            "extension",
            "fly",
            "glute",
            "hamstring",
            "hip",
            "incline",
            "lat",
            "lateral",
            "left",
            "leg",
            "lunge",
            "overhead",
            "press",
            "pull",
            "pulldown",
            "raise",
            "rear",
            "right",
            "row",
            "shoulder",
            "shrug",
            "situp",
            "split",
            "squat",
            "tricep",
        }
        self.spell.word_frequency.load_words(self.exercise_dictionary_words)

        self.exercise_aliases = {
            "bucep": "bicep",
            "bicept": "bicep",
            "bicp": "bicep",
            "hipabductor": "hip abductor",
            "hipadductor": "hip adductor",
            "abducter": "abductor",
            "adducter": "adductor",
        }

        self.word_aliases = {
            "bucep": "bicep",
            "bicept": "bicep",
            "bicp": "bicep",
            "abducter": "abductor",
            "adducter": "adductor",
        }

    def _parse_datetime(self, value: str) -> datetime:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(
            "Date/time must be in YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS format."
        )

    def _capitalize_words(self, text: str) -> str:
        return string.capwords(text.strip())

    def normalize_exercise_name(self, exercise_name: str) -> str:
        cleaned = " ".join(exercise_name.strip().split())
        if not cleaned:
            return ""

        lowered = cleaned.lower()

        if lowered in self.exercise_aliases:
            return self._capitalize_words(self.exercise_aliases[lowered])

        words = lowered.split()
        corrected_words: list[str] = []

        for word in words:
            if word in self.word_aliases:
                corrected_words.append(self.word_aliases[word])
                continue

            correction = self.spell.correction(word)
            corrected_words.append(correction if correction else word)

        normalized = " ".join(corrected_words)

        if normalized in self.exercise_aliases:
            normalized = self.exercise_aliases[normalized]

        return self._capitalize_words(normalized)

    def add_workout(
        self,
        exercise_name: str,
        sets: int,
        reps: int,
        weight: float,
        duration: int,
        workout_datetime: str | None = None,
    ) -> Workout:
        normalized_exercise_name = self.normalize_exercise_name(exercise_name)
        if not normalized_exercise_name:
            raise ValueError("Exercise name is required.")

        sets = int(sets)
        reps = int(reps)
        weight = float(weight)
        duration = int(duration)

        if sets <= 0:
            raise ValueError("Sets must be greater than 0.")
        if reps <= 0:
            raise ValueError("Reps must be greater than 0.")
        if weight < 0:
            raise ValueError("Weight cannot be negative.")
        if duration <= 0:
            raise ValueError("Duration must be greater than 0.")

        timestamp = (
            workout_datetime.strip()
            if workout_datetime
            else datetime.now().strftime(DATETIME_FORMAT)
        )
        parsed_timestamp = self._parse_datetime(timestamp)
        normalized_timestamp = parsed_timestamp.strftime(DATETIME_FORMAT)

        workout = Workout(
            exercise_name=normalized_exercise_name,
            sets=sets,
            reps=reps,
            weight=weight,
            duration=duration,
            workout_datetime=normalized_timestamp,
        )

        workouts = self.repository.load_workouts()
        workouts.append(workout)
        self.repository.save_workouts(workouts)
        return workout

    def get_workouts(self) -> list[Workout]:
        normalized_workouts: list[Workout] = []

        for workout in self.repository.load_workouts():
            normalized_workouts.append(
                Workout(
                    exercise_name=self.normalize_exercise_name(workout.exercise_name),
                    sets=workout.sets,
                    reps=workout.reps,
                    weight=workout.weight,
                    duration=workout.duration,
                    workout_datetime=workout.workout_datetime,
                )
            )

        return sorted(
            normalized_workouts,
            key=lambda workout: self._parse_datetime(workout.workout_datetime),
            reverse=True,
        )

    def get_all_exercise_names(self) -> list[str]:
        names = {
            self.normalize_exercise_name(workout.exercise_name)
            for workout in self.repository.load_workouts()
            if workout.exercise_name.strip()
        }
        return sorted(name for name in names if name)

    def get_workout_summary(self) -> dict[str, float | int | str]:
        workouts = self.get_workouts()
        total_workouts = len(workouts)
        total_sets = sum(workout.sets for workout in workouts)
        total_reps = sum(workout.reps for workout in workouts)
        total_duration = sum(workout.duration for workout in workouts)
        total_volume = sum(workout.sets * workout.reps * workout.weight for workout in workouts)

        if workouts:
            exercise_counts: dict[str, int] = {}
            for workout in workouts:
                exercise_counts[workout.exercise_name] = exercise_counts.get(workout.exercise_name, 0) + 1
            top_exercise = max(exercise_counts, key=exercise_counts.get)
        else:
            top_exercise = "N/A"

        return {
            "total_workouts": total_workouts,
            "total_sets": total_sets,
            "total_reps": total_reps,
            "total_duration": total_duration,
            "top_exercise": top_exercise,
            "total_volume": total_volume,
        }

    def delete_workout(self, workout_to_delete: Workout) -> bool:
        workouts = self.repository.load_workouts()
        for index, workout in enumerate(workouts):
            candidate = Workout(
                exercise_name=self.normalize_exercise_name(workout.exercise_name),
                sets=workout.sets,
                reps=workout.reps,
                weight=workout.weight,
                duration=workout.duration,
                workout_datetime=workout.workout_datetime,
            )
            if candidate == workout_to_delete:
                del workouts[index]
                self.repository.save_workouts(workouts)
                return True
        return False

    def normalize_and_save_existing_workouts(self) -> None:
        workouts = self.repository.load_workouts()
        normalized = [
            Workout(
                exercise_name=self.normalize_exercise_name(workout.exercise_name),
                sets=workout.sets,
                reps=workout.reps,
                weight=workout.weight,
                duration=workout.duration,
                workout_datetime=workout.workout_datetime,
            )
            for workout in workouts
        ]
        self.repository.save_workouts(normalized)


def main() -> None:
    service = WorkoutService()
    service.normalize_and_save_existing_workouts()
    summary = service.get_workout_summary()
    print("Workout summary:")
    print(summary)


if __name__ == "__main__":
    main()
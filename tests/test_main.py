import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import Workout


def test_workout_to_dict():
    workout = Workout(
        exercise_name="Push Ups",
        sets=3,
        reps=12,
        weight=0.0,
        duration=10,
        workout_datetime="2026-04-05T12:30"
    )

    result = workout.to_dict()

    assert result["exercise_name"] == "Push Ups"
    assert result["sets"] == 3
    assert result["reps"] == 12
    assert result["weight"] == 0.0
    assert result["duration"] == 10
    assert result["workout_datetime"] == "2026-04-05T12:30"
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


def test_multiple_workouts_summary_values():
    workouts = [
        {
            "exercise_name": "Push Ups",
            "sets": 3,
            "reps": 12,
            "weight": 0.0,
            "duration": 10,
            "workout_datetime": "2026-04-05T12:30"
        },
        {
            "exercise_name": "Squats",
            "sets": 4,
            "reps": 10,
            "weight": 20.0,
            "duration": 15,
            "workout_datetime": "2026-04-05T13:00"
        }
    ]

    total_workouts = len(workouts)
    total_sets = sum(workout["sets"] for workout in workouts)
    total_reps = sum(workout["reps"] for workout in workouts)
    total_duration = sum(workout["duration"] for workout in workouts)

    assert total_workouts == 2
    assert total_sets == 7
    assert total_reps == 22
    assert total_duration == 25
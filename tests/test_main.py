from main import Workout, WorkoutRepository, WorkoutService


def test_workout_dataclass_fields():
    workout = Workout(
        exercise_name="Push Ups",
        sets=3,
        reps=12,
        weight=0.0,
        duration=10,
        workout_datetime="2026-04-05 12:30",
    )

    assert workout.exercise_name == "Push Ups"
    assert workout.sets == 3
    assert workout.reps == 12
    assert workout.weight == 0.0
    assert workout.duration == 10
    assert workout.workout_datetime == "2026-04-05 12:30"


def test_workout_repository_save_and_load_round_trip(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    workouts = [
        Workout("Push Ups", 3, 12, 0.0, 10, "2026-04-05 12:30"),
        Workout("Squats", 4, 10, 20.0, 15, "2026-04-05 13:00"),
    ]

    repo.save_workouts(workouts)
    loaded = repo.load_workouts()

    assert len(loaded) == 2
    assert loaded[0].exercise_name == "Push Ups"
    assert loaded[0].sets == 3
    assert loaded[0].reps == 12
    assert loaded[0].weight == 0.0
    assert loaded[0].duration == 10
    assert loaded[0].workout_datetime == "2026-04-05 12:30"
    assert loaded[1].exercise_name == "Squats"
    assert loaded[1].sets == 4
    assert loaded[1].reps == 10
    assert loaded[1].weight == 20.0
    assert loaded[1].duration == 15
    assert loaded[1].workout_datetime == "2026-04-05 13:00"


def test_workout_service_summary(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("Push Ups", 3, 12, 0.0, 10, "2026-04-05 12:30"),
        Workout("Squats", 4, 10, 20.0, 15, "2026-04-05 13:00"),
    ])
    service = WorkoutService(repo)

    summary = service.get_workout_summary()

    assert summary["total_workouts"] == 2
    assert summary["total_sets"] == 7
    assert summary["total_reps"] == 22
    assert summary["total_duration"] == 25
    assert summary["top_exercise"] in {"Push Ups", "Squats"}
    assert summary["total_volume"] == 800.0


def test_workout_service_delete_workout(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("Push Ups", 3, 12, 0.0, 10, "2026-04-05 12:30"),
        Workout("Squats", 4, 10, 20.0, 15, "2026-04-05 13:00"),
    ])
    service = WorkoutService(repo)

    assert service.delete_workout(0) is True
    remaining = repo.load_workouts()
    assert len(remaining) == 1
    assert remaining[0].exercise_name == "Squats"
    assert service.delete_workout(5) is False 
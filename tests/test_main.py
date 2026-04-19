import pytest

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
        Workout("Squat", 4, 10, 20.0, 15, "2026-04-05 13:00"),
    ]

    repo.save_workouts(workouts)
    loaded = repo.load_workouts()

    assert len(loaded) == 2
    assert loaded[0] == workouts[0]
    assert loaded[1] == workouts[1]


def test_normalize_exercise_name_corrects_common_typos(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    assert service.normalize_exercise_name("bucep curl") == "Bicep Curl"
    assert service.normalize_exercise_name("hip abductor") == "Hip Abductor"
    assert service.normalize_exercise_name("hip adductor") == "Hip Adductor"


def test_normalize_exercise_name_auto_capitalizes_each_word(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    assert service.normalize_exercise_name("leg press") == "Leg Press"
    assert service.normalize_exercise_name("left bicep curl") == "Left Bicep Curl"
    assert service.normalize_exercise_name("bench press") == "Bench Press"


def test_add_workout_saves_normalized_exercise_name(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    saved = service.add_workout(
        exercise_name="bucep curl",
        sets=3,
        reps=10,
        weight=25.0,
        duration=20,
        workout_datetime="2026-04-05 12:30",
    )

    assert saved.exercise_name == "Bicep Curl"

    workouts = service.repository.load_workouts()
    assert len(workouts) == 1
    assert workouts[0].exercise_name == "Bicep Curl"


def test_add_workout_rejects_blank_exercise_name(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    with pytest.raises(ValueError, match="Exercise name is required"):
        service.add_workout(
            exercise_name="   ",
            sets=3,
            reps=10,
            weight=25.0,
            duration=20,
            workout_datetime="2026-04-05 12:30",
        )


def test_add_workout_rejects_invalid_numeric_values(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    with pytest.raises(ValueError, match="Sets must be greater than 0"):
        service.add_workout(
            exercise_name="Bench Press",
            sets=0,
            reps=10,
            weight=135.0,
            duration=20,
            workout_datetime="2026-04-05 12:30",
        )

    with pytest.raises(ValueError, match="Reps must be greater than 0"):
        service.add_workout(
            exercise_name="Bench Press",
            sets=3,
            reps=0,
            weight=135.0,
            duration=20,
            workout_datetime="2026-04-05 12:30",
        )

    with pytest.raises(ValueError, match="Weight cannot be negative"):
        service.add_workout(
            exercise_name="Bench Press",
            sets=3,
            reps=10,
            weight=-1.0,
            duration=20,
            workout_datetime="2026-04-05 12:30",
        )

    with pytest.raises(ValueError, match="Duration must be greater than 0"):
        service.add_workout(
            exercise_name="Bench Press",
            sets=3,
            reps=10,
            weight=135.0,
            duration=0,
            workout_datetime="2026-04-05 12:30",
        )


def test_get_workouts_returns_newest_first_and_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("hip adductor", 3, 10, 40.0, 15, "2026-04-05 09:00"),
        Workout("bucep curl", 4, 8, 25.0, 20, "2026-04-06 09:00"),
    ])
    service = WorkoutService(repo)

    workouts = service.get_workouts()

    assert len(workouts) == 2
    assert workouts[0].exercise_name == "Bicep Curl"
    assert workouts[1].exercise_name == "Hip Adductor"
    assert workouts[0].workout_datetime == "2026-04-06 09:00"
    assert workouts[1].workout_datetime == "2026-04-05 09:00"


def test_get_all_exercise_names_returns_unique_sorted_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("bucep curl", 2, 8, 20.0, 10, "2026-04-05 09:00"),
        Workout("Bicep Curl", 3, 10, 25.0, 12, "2026-04-05 10:00"),
        Workout("hip abductor", 3, 12, 40.0, 15, "2026-04-05 11:00"),
        Workout("hip adductor", 3, 12, 40.0, 15, "2026-04-05 12:00"),
    ])
    service = WorkoutService(repo)

    names = service.get_all_exercise_names()

    assert names == ["Bicep Curl", "Hip Abductor", "Hip Adductor"]


def test_get_workout_summary_uses_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("bucep curl", 3, 10, 25.0, 20, "2026-04-05 09:00"),
        Workout("bicep curl", 2, 12, 20.0, 15, "2026-04-05 10:00"),
        Workout("hip abductor", 3, 8, 40.0, 12, "2026-04-05 11:00"),
    ])
    service = WorkoutService(repo)

    summary = service.get_workout_summary()

    assert summary["total_workouts"] == 3
    assert summary["total_sets"] == 8
    assert summary["total_reps"] == 30
    assert summary["total_duration"] == 47
    assert summary["total_volume"] == 2190.0
    assert summary["top_exercise"] == "Bicep Curl"


def test_delete_workout_matches_normalized_record(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    original = Workout("bucep curl", 3, 10, 25.0, 20, "2026-04-05 09:00")
    repo.save_workouts([original])

    service = WorkoutService(repo)

    normalized_target = Workout("Bicep Curl", 3, 10, 25.0, 20, "2026-04-05 09:00")
    deleted = service.delete_workout(normalized_target)

    assert deleted is True
    assert repo.load_workouts() == []


def test_normalize_and_save_existing_workouts_rewrites_saved_data(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([
        Workout("bucep curl", 2, 8, 20.0, 10, "2026-04-05 09:00"),
        Workout("hip abductor", 3, 12, 40.0, 15, "2026-04-05 11:00"),
        Workout("hip adductor", 3, 12, 40.0, 15, "2026-04-05 12:00"),
    ])

    service = WorkoutService(repo)
    service.normalize_and_save_existing_workouts()

    rewritten = repo.load_workouts()

    assert rewritten[0].exercise_name == "Bicep Curl"
    assert rewritten[1].exercise_name == "Hip Abductor"
    assert rewritten[2].exercise_name == "Hip Adductor"
import json
import uuid

import pytest

from main import Workout, WorkoutDataError, WorkoutRepository, WorkoutService


def make_workout(
    exercise_name: str = "Push Ups",
    sets: int = 3,
    reps: int = 12,
    weight: float = 0.0,
    duration: int = 10,
    workout_datetime: str = "2026-04-05 12:30",
    workout_id: str | None = None,
) -> Workout:
    return Workout(
        id=workout_id or str(uuid.uuid4()),
        exercise_name=exercise_name,
        sets=sets,
        reps=reps,
        weight=weight,
        duration=duration,
        workout_datetime=workout_datetime,
    )


def test_workout_dataclass_fields():
    workout = make_workout()

    assert workout.id
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
        make_workout(
            exercise_name="Push Ups",
            sets=3,
            reps=12,
            weight=0.0,
            duration=10,
            workout_datetime="2026-04-05 12:30",
            workout_id="id-1",
        ),
        make_workout(
            exercise_name="Squat",
            sets=4,
            reps=10,
            weight=20.0,
            duration=15,
            workout_datetime="2026-04-05 13:00",
            workout_id="id-2",
        ),
    ]

    repo.save_workouts(workouts)
    loaded = repo.load_workouts()

    assert len(loaded) == 2
    assert loaded[0] == workouts[0]
    assert loaded[1] == workouts[1]


def test_repository_raises_on_corrupted_json(tmp_path):
    file_path = tmp_path / "workouts.json"
    file_path.write_text("{not valid json", encoding="utf-8")

    repo = WorkoutRepository(file_path)

    with pytest.raises(WorkoutDataError, match="corrupted"):
        repo.load_workouts()


def test_repository_raises_on_non_list_json_root(tmp_path):
    file_path = tmp_path / "workouts.json"
    file_path.write_text(json.dumps({"bad": "shape"}), encoding="utf-8")

    repo = WorkoutRepository(file_path)

    with pytest.raises(WorkoutDataError, match="JSON list"):
        repo.load_workouts()


def test_repository_raises_on_invalid_record_fields(tmp_path):
    file_path = tmp_path / "workouts.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "id": "broken-1",
                    "exercise_name": "Bench Press",
                    "sets": "not-a-number",
                    "reps": 10,
                    "weight": 135.0,
                    "duration": 20,
                    "workout_datetime": "2026-04-05 12:30",
                }
            ]
        ),
        encoding="utf-8",
    )

    repo = WorkoutRepository(file_path)

    with pytest.raises(WorkoutDataError, match="invalid field values"):
        repo.load_workouts()


def test_repository_generates_id_for_legacy_record_without_id(tmp_path):
    file_path = tmp_path / "workouts.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "exercise_name": "Bench Press",
                    "sets": 3,
                    "reps": 10,
                    "weight": 135.0,
                    "duration": 20,
                    "workout_datetime": "2026-04-05 12:30",
                }
            ]
        ),
        encoding="utf-8",
    )

    repo = WorkoutRepository(file_path)
    loaded = repo.load_workouts()

    assert len(loaded) == 1
    assert loaded[0].id
    assert loaded[0].exercise_name == "Bench Press"


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


def test_normalize_exercise_name_does_not_overcorrect_short_words(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    assert service.normalize_exercise_name("ab row") == "Ab Row"


def test_add_workout_saves_normalized_exercise_name_and_id(tmp_path):
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
    assert saved.id

    workouts = service.repository.load_workouts()
    assert len(workouts) == 1
    assert workouts[0].exercise_name == "Bicep Curl"
    assert workouts[0].id == saved.id


def test_add_workout_rejects_blank_exercise_name(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    with pytest.raises(ValueError, match="Exercise name is required"):
        service.add_workout(
            exercise_name=" ",
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


def test_add_workout_rejects_non_numeric_input(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    with pytest.raises(ValueError, match="must be valid numbers"):
        service.add_workout(
            exercise_name="Bench Press",
            sets="three",
            reps=10,
            weight=135.0,
            duration=20,
            workout_datetime="2026-04-05 12:30",
        )


def test_add_workout_rejects_invalid_datetime_format(tmp_path):
    file_path = tmp_path / "workouts.json"
    service = WorkoutService(WorkoutRepository(file_path))

    with pytest.raises(ValueError, match="Date/time must be in"):
        service.add_workout(
            exercise_name="Bench Press",
            sets=3,
            reps=10,
            weight=135.0,
            duration=20,
            workout_datetime="04/05/2026 12:30 PM",
        )


def test_get_workouts_returns_newest_first_and_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts(
        [
            make_workout(
                exercise_name="hip adductor",
                sets=3,
                reps=10,
                weight=40.0,
                duration=15,
                workout_datetime="2026-04-05 09:00",
                workout_id="id-old",
            ),
            make_workout(
                exercise_name="bucep curl",
                sets=4,
                reps=8,
                weight=25.0,
                duration=20,
                workout_datetime="2026-04-06 09:00",
                workout_id="id-new",
            ),
        ]
    )
    service = WorkoutService(repo)

    workouts = service.get_workouts()

    assert len(workouts) == 2
    assert workouts[0].exercise_name == "Bicep Curl"
    assert workouts[1].exercise_name == "Hip Adductor"
    assert workouts[0].workout_datetime == "2026-04-06 09:00"
    assert workouts[1].workout_datetime == "2026-04-05 09:00"
    assert workouts[0].id == "id-new"


def test_get_all_exercise_names_returns_unique_sorted_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts(
        [
            make_workout(
                exercise_name="bucep curl",
                sets=2,
                reps=8,
                weight=20.0,
                duration=10,
                workout_datetime="2026-04-05 09:00",
                workout_id="id-1",
            ),
            make_workout(
                exercise_name="Bicep Curl",
                sets=3,
                reps=10,
                weight=25.0,
                duration=12,
                workout_datetime="2026-04-05 10:00",
                workout_id="id-2",
            ),
            make_workout(
                exercise_name="hip abductor",
                sets=3,
                reps=12,
                weight=40.0,
                duration=15,
                workout_datetime="2026-04-05 11:00",
                workout_id="id-3",
            ),
            make_workout(
                exercise_name="hip adductor",
                sets=3,
                reps=12,
                weight=40.0,
                duration=15,
                workout_datetime="2026-04-05 12:00",
                workout_id="id-4",
            ),
        ]
    )
    service = WorkoutService(repo)

    names = service.get_all_exercise_names()

    assert names == ["Bicep Curl", "Hip Abductor", "Hip Adductor"]


def test_get_workout_summary_uses_normalized_names(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts(
        [
            make_workout(
                exercise_name="bucep curl",
                sets=3,
                reps=10,
                weight=25.0,
                duration=20,
                workout_datetime="2026-04-05 09:00",
                workout_id="id-1",
            ),
            make_workout(
                exercise_name="bicep curl",
                sets=2,
                reps=12,
                weight=20.0,
                duration=15,
                workout_datetime="2026-04-05 10:00",
                workout_id="id-2",
            ),
            make_workout(
                exercise_name="hip abductor",
                sets=3,
                reps=8,
                weight=40.0,
                duration=12,
                workout_datetime="2026-04-05 11:00",
                workout_id="id-3",
            ),
        ]
    )
    service = WorkoutService(repo)

    summary = service.get_workout_summary()

    assert summary["total_workouts"] == 3
    assert summary["total_sets"] == 8
    assert summary["total_reps"] == 30
    assert summary["total_duration"] == 47
    assert summary["total_volume"] == 2190.0
    assert summary["top_exercise"] == "Bicep Curl"


def test_get_workout_by_id_returns_expected_record(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    target = make_workout(
        exercise_name="Deadlift",
        sets=5,
        reps=5,
        weight=225.0,
        duration=18,
        workout_datetime="2026-04-05 07:30",
        workout_id="target-id",
    )
    repo.save_workouts([target])
    service = WorkoutService(repo)

    resolved = service.get_workout_by_id("target-id")

    assert resolved is not None
    assert resolved.id == "target-id"
    assert resolved.exercise_name == "Deadlift"


def test_delete_workout_by_id_deletes_only_matching_record(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)

    keep_workout = make_workout(
        exercise_name="Squat",
        sets=4,
        reps=8,
        weight=185.0,
        duration=20,
        workout_datetime="2026-04-05 08:00",
        workout_id="keep-id",
    )
    delete_workout = make_workout(
        exercise_name="Squat",
        sets=4,
        reps=8,
        weight=185.0,
        duration=20,
        workout_datetime="2026-04-05 08:00",
        workout_id="delete-id",
    )

    repo.save_workouts([keep_workout, delete_workout])
    service = WorkoutService(repo)

    deleted = service.delete_workout_by_id("delete-id")
    remaining = repo.load_workouts()

    assert deleted is True
    assert len(remaining) == 1
    assert remaining[0].id == "keep-id"


def test_delete_workout_by_id_returns_false_for_missing_id(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts([make_workout(workout_id="existing-id")])
    service = WorkoutService(repo)

    deleted = service.delete_workout_by_id("missing-id")

    assert deleted is False
    assert len(repo.load_workouts()) == 1


def test_delete_workout_falls_back_to_field_match_when_id_blank(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)

    original = make_workout(
        exercise_name="bucep curl",
        sets=3,
        reps=10,
        weight=25.0,
        duration=20,
        workout_datetime="2026-04-05 09:00",
        workout_id="stored-id",
    )
    repo.save_workouts([original])

    service = WorkoutService(repo)

    normalized_target = Workout(
        id="",
        exercise_name="Bicep Curl",
        sets=3,
        reps=10,
        weight=25.0,
        duration=20,
        workout_datetime="2026-04-05 09:00",
    )
    deleted = service.delete_workout(normalized_target)

    assert deleted is True
    assert repo.load_workouts() == []


def test_normalize_and_save_existing_workouts_rewrites_saved_data(tmp_path):
    file_path = tmp_path / "workouts.json"
    repo = WorkoutRepository(file_path)
    repo.save_workouts(
        [
            make_workout(
                exercise_name="bucep curl",
                sets=2,
                reps=8,
                weight=20.0,
                duration=10,
                workout_datetime="2026-04-05 09:00:00",
                workout_id="id-1",
            ),
            make_workout(
                exercise_name="hip abductor",
                sets=3,
                reps=12,
                weight=40.0,
                duration=15,
                workout_datetime="2026-04-05 11:00",
                workout_id="id-2",
            ),
            make_workout(
                exercise_name="hip adductor",
                sets=3,
                reps=12,
                weight=40.0,
                duration=15,
                workout_datetime="2026-04-05 12:00",
                workout_id="id-3",
            ),
        ]
    )

    service = WorkoutService(repo)
    rewritten = service.normalize_and_save_existing_workouts()

    assert rewritten[0].exercise_name == "Bicep Curl"
    assert rewritten[0].id == "id-1"
    assert rewritten[0].workout_datetime == "2026-04-05 09:00"

    persisted = repo.load_workouts()
    assert persisted[0].exercise_name == "Bicep Curl"
    assert persisted[1].exercise_name == "Hip Abductor"
    assert persisted[2].exercise_name == "Hip Adductor"


def test_load_workouts_empty_file_returns_empty_list(tmp_path):
    file_path = tmp_path / "workouts.json"
    file_path.write_text("", encoding="utf-8")

    repo = WorkoutRepository(file_path)

    assert repo.load_workouts() == []
import pytest
from habit_tracker.habit_manager import HabitManager


def seed_habits(manager: HabitManager):
    manager.add_habit("10 min cardio")
    manager.add_habit("drink 2L of water")
    manager.add_habit("read 1 chapter of quran")


def test_add_and_list(tmp_path):
    data = tmp_path / "habits.json"
    hm = HabitManager(data)

    new_habit = hm.add_habit("10 min cardio")
    assert new_habit.name == "10 min cardio"

    habits = hm.list_habits()
    assert len(habits) == 1
    assert habits[0].name == "10 min cardio"


def test_add_and_delete(tmp_path):
    data = tmp_path / "habits.json"
    hm = HabitManager(data)

    new_habit = hm.add_habit("10 min cardio")
    assert new_habit.name == "10 min cardio"

    habits = hm.list_habits()
    assert len(habits) == 1

    deleted_habit = hm.delete_habit(new_habit.id)
    assert deleted_habit.name == "10 min cardio"

    habits = hm.list_habits()
    assert len(habits) == 0


def test_add_duplicate(tmp_path):
    data = tmp_path / "habits.json"
    hm = HabitManager(data)

    new_habit = hm.add_habit("10 min cardio")
    assert new_habit.name == "10 min cardio"

    habits = hm.list_habits()
    assert len(habits) == 1
    assert habits[0].name == "10 min cardio"

    with pytest.raises(ValueError, match="Habit already exists!"):
        hm.add_habit("10 min cardio")


def test_archive_habit(tmp_path):
    data = tmp_path / "habits.json"
    hm = HabitManager(data)

    new_habit = hm.add_habit("10 min cardio")
    assert new_habit.name == "10 min cardio"

    new_habit = hm.archive_habit_by_id(new_habit.id)
    assert new_habit.archived == True


def test_undo_last_delete(tmp_path):
    hm = HabitManager(tmp_path/"h.json")
    h1 = hm.add_habit("cardio")
    hm.delete_habit(h1.id)
    assert hm.list_habits() == []
    restored = hm.restore_last_habit()
    assert restored.id == h1.id
    assert len(hm.list_habits()) == 1

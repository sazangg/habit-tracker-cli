from datetime import date
from habit_tracker.entry_manager import EntryManager
import pytest


def test_add_and_list(tmp_path):
    entry_data = tmp_path / "entries.json"
    habit_data = tmp_path / "habits.json"

    em = EntryManager(entry_data, habit_data)

    new_habit = em._hm.add_habit("10 min cardio")
    assert new_habit.name == "10 min cardio"

    new_entry = em.add_entry(
        new_habit.id, date_="2025-05-01", note="Done for today")
    assert new_entry.habit_id == new_habit.id
    assert new_entry.note == "Done for today"
    assert new_entry.date_ == date.fromisoformat("2025-05-01")

    entries = em.list_entries()
    assert len(entries) == 1
    assert entries[0].note == "Done for today"


def test_add_invalid_habit_id(tmp_path):
    entry_data = tmp_path / "entries.json"
    habit_data = tmp_path / "habits.json"

    em = EntryManager(entry_data, habit_data)

    with pytest.raises(ValueError):
        em.add_entry("invalid_id")


def test_delete_entry(tmp_path):
    entry_data = tmp_path / "entries.json"
    habit_data = tmp_path / "habits.json"

    em = EntryManager(entry_data, habit_data)
    new_habit = em._hm.add_habit("10 min cardio")
    new_entry = em.add_entry(
        new_habit.id, date_="2025-05-01", note="Done for today")

    deleted_entry = em.delete_entry(new_entry.id)
    assert deleted_entry.id == new_entry.id

    entries = em.list_entries()
    assert len(entries) == 0

    em = EntryManager(entry_data, habit_data)
    entries = em.list_entries()
    assert len(entries) == 0

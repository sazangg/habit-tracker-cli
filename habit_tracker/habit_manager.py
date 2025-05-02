import csv
from enum import Enum
from pathlib import Path
from typing import List, Union

from .models import Habit
from .crypto import EncryptedJSONRepo


class IMPORT_MODE(Enum):
    add = "add"
    replace = "replace"
    merge = "merge"


class HabitManager:
    def __init__(self, path: Path):
        self._repo = HabitRepository(path)
        self._habits = self._repo.load_habits()

    def list_habits(self) -> List[Habit]:
        return list(self._habits)

    def save_habits(self):
        self._repo.save_habits(self._habits)

    def add_habit(self, name: str, priority: int = 3) -> "Habit":
        if self.is_duplicate_habit(name):
            raise ValueError("Habit already exists!")
        new_habit = Habit(name, priority=priority)
        self._habits.append(new_habit)
        self.save_habits()
        return new_habit

    def delete_habit(self, habit_id: str) -> "Habit":
        habit_to_delete = self.find_habit_by_id(habit_id)
        if not habit_to_delete:
            raise ValueError(f"No habit to delete found for id: {habit_id}")
        self._habits.remove(habit_to_delete)
        self.save_habits()
        return habit_to_delete

    def archive_habit_by_id(self, habit_id: str) -> "Habit":
        habit_to_archive = self.find_habit_by_id(habit_id)
        if not habit_to_archive:
            raise ValueError(f"No habit to archive found for id: {habit_id}")
        habit_to_archive.archived = True
        self.save_habits()
        return habit_to_archive

    def find_habit_by_id(self, habit_id: str) -> Union[Habit, None]:
        for habit in self._habits:
            if habit.id == habit_id:
                return habit
        return None

    def find_habit_by_name(self, habit_name: str) -> Union[Habit, None]:
        for h in self._habits:
            if h.name == habit_name:
                return h
        return None

    def is_duplicate_habit(self, name: str) -> bool:
        return name.lower() in [h.name.lower() for h in self._habits]

    def export_habits(self) -> None:
        field_names = ['id', 'name', 'priority', 'archived', 'created_at']
        data = [h.to_dict() for h in self._habits]
        self._repo.export_habits_to_csv(data, field_names=field_names)

    def import_habits(self, mode: IMPORT_MODE = IMPORT_MODE.add) -> None:
        imported_habits = self._repo.import_habits_from_csv()

        if mode == IMPORT_MODE.add:
            for habit in imported_habits:
                if not self.find_habit_by_id(habit.id):
                    self._habits.append(habit)
        elif mode == IMPORT_MODE.merge:
            for habit in imported_habits:
                existing_habit = self.find_habit_by_id(habit.id)
                if existing_habit:
                    existing_habit.name = habit.name
                    existing_habit.priority = habit.priority
                    existing_habit.archived = habit.archived
                    existing_habit.created_at = habit.created_at
                else:
                    self._habits.append(habit)
        elif mode == IMPORT_MODE.replace:
            self._habits = imported_habits

        self.save_habits()


class HabitRepository:
    def __init__(self, path: Path):
        self._path = Path(path)

    def load_habits(self) -> List[Habit]:
        json_data = EncryptedJSONRepo.load_data(self._path)
        return [Habit.from_dict(h) for h in json_data if h is not None]

    def save_habits(self, habits: List[Habit]) -> None:
        data = [h.to_dict() for h in habits]

        EncryptedJSONRepo.save_data(data, self._path)

    def export_habits_to_csv(self, habits_dict, field_names) -> None:
        with self._path.with_suffix("").with_suffix(".csv").open(mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(habits_dict)

    def import_habits_from_csv(self) -> List[Habit]:
        csv_path = self._path.with_suffix("").with_suffix(".csv")
        if not csv_path.exists() or csv_path.stat().st_size == 0:
            return []

        with csv_path.open(mode="r", newline="", encoding="utf-8") as f:
            dict_reader = csv.DictReader(f)
            return [Habit.from_dict(row) for row in dict_reader if row]

    def append_log(self):
        pass

    def pop_log(self):
        pass

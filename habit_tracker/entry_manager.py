from datetime import date
import json
from pathlib import Path
from typing import List, Union

from filelock import FileLock

from .models import Entry
from .habit_manager import HabitManager
from .crypto import EncryptedJSONRepo


class EntryManager:
    def __init__(self, path: Path, habits_path: Path):
        self._repo = EntryRepository(path)
        self._hm = HabitManager(habits_path)
        self._entries = self._repo.load_entries()

    def list_entries(self) -> List[Entry]:
        return list(self._entries)

    def save_entries(self) -> None:
        self._repo.save_entries(self._entries)

    def add_entry(self, habit_id: str, date_: str = "", note: str = "") -> "Entry":
        entry_habit = self._hm.find_habit_by_id(habit_id)
        if not entry_habit:
            raise ValueError(f"No habit matches the specified id: {habit_id}")
        entry_date = date.fromisoformat(date_) if date_ else date.today()
        new_entry = Entry(habit_id, date_=entry_date, note=note)
        self._entries.append(new_entry)
        self.save_entries()
        return new_entry

    def delete_entry(self, entry_id: str) -> "Entry":
        entry_to_delete = self.find_entry_by_id(entry_id)
        if not entry_to_delete:
            raise ValueError(f"No habit to delete found for id: {entry_id}")
        self._entries.remove(entry_to_delete)
        self.save_entries()
        return entry_to_delete

    def find_entry_by_id(self, entry_id: str) -> Union[Entry, None]:
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None


class EntryRepository:
    def __init__(self, path: Path):
        self._path = Path(path)

    def load_entries(self) -> List[Entry]:
        json_data = EncryptedJSONRepo.load_data(self._path)
        return [Entry.from_dict(e) for e in json_data if e is not None]

    def save_entries(self, entries: List[Entry]) -> None:
        data = [e.to_dict() for e in entries]

        EncryptedJSONRepo.save_data(data, self._path)

    def append_log(self):
        pass

    def pop_log(self):
        pass

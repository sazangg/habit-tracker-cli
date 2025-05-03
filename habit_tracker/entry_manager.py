import csv
from datetime import date
import json
from pathlib import Path
from typing import List, Union

from filelock import FileLock

from .models import Entry
from .habit_manager import HabitManager, IMPORT_MODE
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
        self._repo.append_log(entry_to_delete)
        return entry_to_delete

    def restore_last_entry(self) -> "Entry":
        recovered_entry = self._repo.pop_log()
        if self.find_entry_by_id(recovered_entry.id):
            raise ValueError("Cannot undo - id already exists!")
        self._entries.append(recovered_entry)
        self.save_entries()
        return recovered_entry

    def find_entry_by_id(self, entry_id: str) -> Union[Entry, None]:
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    def export_entries(self, export_path: Path | None = None) -> None:
        field_names = ['id', 'habit_id', 'date_', 'note']
        data = [e.to_dict() for e in self._entries]
        return self._repo.export_entries_to_csv(data, field_names, export_path)

    def import_entries(self, mode: IMPORT_MODE = IMPORT_MODE.add):
        imported_entries = self._repo.import_entries_from_csv()
        imported_stats = {"added": 0, "updated": 0, "replaced": 0}
        if mode == IMPORT_MODE.add:
            for entry in imported_entries:
                if not self.find_entry_by_id(entry.id):
                    self._entries.append(entry)
                    imported_stats["added"] += 1
        elif mode == IMPORT_MODE.merge:
            for entry in imported_entries:
                existing_entry = self.find_entry_by_id(entry.id)
                if existing_entry:
                    existing_entry.__dict__.update(entry.__dict__)
                    imported_stats["updated"] += 1
                else:
                    self._entries.append(entry)
                    imported_stats["added"] += 1
        elif mode == IMPORT_MODE.replace:
            imported_stats["replaced"] = len(self._entries)
            imported_stats["added"] = len(imported_entries)
            self._entries = imported_entries

        self.save_entries()
        return imported_stats


class EntryRepository:
    def __init__(self, path: Path):
        self._path = Path(path)

    def load_entries(self) -> List[Entry]:
        json_data = EncryptedJSONRepo.load_data(self._path)
        return [Entry.from_dict(e) for e in json_data if e is not None]

    def save_entries(self, entries: List[Entry]) -> None:
        data = [e.to_dict() for e in entries]

        EncryptedJSONRepo.save_data(data, self._path)

    def export_entries_to_csv(self, entries_dict, field_names, export_path: Path | None = None) -> Path:
        target = (export_path or self._path.with_suffix(
            "")).with_suffix(".csv")
        target.parent.mkdir(parents=True, exist_ok=True)

        with target.open(mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(entries_dict)

        return target

    def import_entries_from_csv(self) -> List[Entry]:
        csv_path = self._path.with_suffix("").with_suffix(".csv")
        if not csv_path.exists() or csv_path.stat().st_size == 0:
            return []

        with csv_path.open(mode="r", newline="", encoding="utf-8") as f:
            dict_reader = csv.DictReader(f)
            return [Entry.from_dict(row) for row in dict_reader if row]

    def append_log(self, entry_to_log: Entry) -> None:
        log_path = self._path.with_suffix("").with_suffix(".log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        lock = FileLock(log_path.with_suffix(".lock"))
        with lock, log_path.open(mode="a", newline="", encoding="utf-8") as f:
            f.write(json.dumps(entry_to_log.to_dict()) + "\n")

    def pop_log(self) -> "Entry":
        log_path = self._path.with_suffix("").with_suffix(".log")
        if not log_path.exists() or log_path.stat().st_size == 0:
            raise ValueError("Nothing to undo")
        lines = log_path.read_text().splitlines()
        last, *rest = lines[::-1]
        lock = FileLock(log_path.with_suffix(".lock"))
        with lock:
            log_path.write_text("\n".join(rest[::-1]) + ("\n" if rest else ""))
        return Entry.from_dict(json.loads(last))

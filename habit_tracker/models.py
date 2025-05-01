from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, date
from uuid import uuid4


@dataclass
class Habit:
    name: str
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).astimezone())
    priority: int = 3
    archived: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Habit":
        habit = d.copy()
        habit["created_at"] = datetime.fromisoformat(d["created_at"])
        return cls(**habit)


@dataclass
class Entry:
    habit_id: str
    date_: date = field(
        default_factory=lambda: date.today())
    id: str = field(default_factory=lambda: uuid4().hex)
    note: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["date_"] = self.date_.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Entry":
        entry = d.copy()
        entry["date_"] = date.fromisoformat(d["date_"])
        return cls(**entry)

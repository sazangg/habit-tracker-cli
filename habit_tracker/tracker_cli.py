from pathlib import Path
from .entry_cli import app as entry_app
from .habit_cli import app as habit_app
import typer

from .habit_manager import HabitManager
from .entry_manager import EntryManager

app = typer.Typer()
app.add_typer(habit_app, name="habit")
app.add_typer(entry_app, name="entry")


@app.callback()
def init(
    ctx: typer.Context,
    habits_path: Path = typer.Option(
        Path.home()/"habits.json", envvar="HABITS_PATH"),
    entries_path: Path = typer.Option(
        Path.home()/"entries.json", envvar="ENTRIES_PATH"),
):
    ctx.obj = {
        "habit_manager": HabitManager(habits_path),
        "entry_manager": EntryManager(entries_path, habits_path)
    }


def main():
    app()


if __name__ == "__main__":
    app()

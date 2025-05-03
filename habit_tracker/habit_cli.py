import json
import os
from pathlib import Path
import typer
from .habit_manager import HabitManager
app = typer.Typer(help="Manage habits")


@app.callback()
def initialize(ctx: typer.Context):
    env_path = os.getenv("HABITS_PATH")

    if env_path:
        ctx.obj = HabitManager(Path(env_path))
    else:
        default_path = Path.home() / "habits.json"
        ctx.obj = HabitManager(default_path)


@app.command("list")
def list_habits(ctx: typer.Context):
    habits = [h.to_dict() for h in ctx.obj.list_habits()]

    typer.echo(json.dumps(habits, indent=2))
    typer.Exit(code=0)


@app.command("add")
def add_habit(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Habit name"),
    priority: int = typer.Option(
        3, "--priority", "-p", help="Priority between 1 and 5")
):
    try:
        new_habit = ctx.obj.add_habit(name, priority)
        typer.echo(json.dumps(new_habit.to_dict(), indent=2))
        typer.Exit(code=0)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)

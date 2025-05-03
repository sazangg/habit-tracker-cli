import json
from pathlib import Path
import typer
from .habit_manager import IMPORT_MODE

app = typer.Typer(help="Manage habits")


@app.callback()
def habit_init(ctx: typer.Context):
    ctx.obj = ctx.parent.obj["habit_manager"]


@app.command("list")
def list_habits(ctx: typer.Context):
    habits = [h.to_dict() for h in ctx.obj.list_habits()]
    typer.echo(json.dumps(habits, indent=2))


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
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)


@app.command("delete")
def delete_habit(ctx: typer.Context, habit_id: str):
    try:
        habit_to_delete = ctx.obj.delete_habit(habit_id)
        typer.echo(
            f"Deleted habit: {habit_to_delete.name} with id: {habit_to_delete.id}")
    except ValueError as e:
        typer.echo(str(e), err=True)
        typer.Exit(code=1)


@app.command("undo")
def restore_last_habit(ctx: typer.Context):
    try:
        recovered_habit = ctx.obj.restore_last_habit()
        typer.echo(f"Successfully recovered last deleted habit.")
        typer.echo(json.dumps(recovered_habit.to_dict(), indent=2))
    except ValueError as e:
        typer.echo(str(e), err=True)
        typer.Exit(code=1)


@app.command("export")
def export_habits(ctx: typer.Context, file: Path = typer.Option(None, "-f", "--file")):
    out_path = ctx.obj.export_habits(file)
    typer.echo(f"Exported to {out_path}.")


@app.command("import")
def import_habits(
    ctx: typer.Context,
    mode: IMPORT_MODE = typer.Option(
        IMPORT_MODE.add, "-m", "--mode", case_sensitive=False)
):
    stats = ctx.obj.import_habits(mode)
    typer.echo(
        f"Habits imported successfully: {stats['added']} added, {stats['updated']} updated, {stats['replaced']} replaced.")

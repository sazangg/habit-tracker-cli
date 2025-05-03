import json
import typer

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

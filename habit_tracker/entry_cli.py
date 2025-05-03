import json
from pathlib import Path
from typing import Literal
import typer

app = typer.Typer(help="Manage habit entries")


@app.callback()
def entry_init(ctx: typer.Context):
    ctx.obj = ctx.parent.obj["entry_manager"]


@app.command("list")
def list_entries(ctx: typer.Context):
    entries = [e.to_dict() for e in ctx.obj.list_entries()]
    typer.echo(json.dumps(entries, indent=2))
    typer.Exit(code=0)


@app.command("add")
def add_entry(
    ctx: typer.Context,
    habit_id: str,
    date_: str = typer.Option("", "-d", "--date"),
    note: str = typer.Option("", "-n", "--notes")
):
    try:
        new_entry = ctx.obj.add_entry(habit_id, date_=date_, note=note)
        typer.echo(json.dumps(new_entry.to_dict(), indent=2))
    except ValueError as e:
        typer.echo(str(e), err=True)
        typer.Exit(code=1)


@app.command("delete")
def delete_entry(ctx: typer.Context, entry_id: str):
    try:
        entry_to_delete = ctx.obj.delete_entry(entry_id)
        typer.echo(
            f"Deleted entry with id: {entry_to_delete.id}")
    except ValueError as e:
        typer.echo(str(e), err=True)
        typer.Exit(code=1)


@app.command("undo")
def restore_last_entry(ctx: typer.Context):
    try:
        recovered_entry = ctx.obj.restore_last_entry()
        typer.echo(f"Successfully recovered last deleted entry.")
        typer.echo(json.dumps(recovered_entry.to_dict(), indent=2))
    except ValueError as e:
        typer.echo(str(e), err=True)
        typer.Exit(code=1)


@app.command("export")
def export_entries(ctx: typer.Context, file: Path = typer.Option(None, "-f", "--file")):
    out_path = ctx.obj.export_entries(file)
    typer.echo(f"Exported to {out_path}.")


@app.command("import")
def import_entries(
    ctx: typer.Context,
    mode: Literal["add", "merge", "replace"] = typer.Option(
        "add", "-m", "--mode", case_sensitive=False)
):
    stats = ctx.obj.import_entries(mode)
    typer.echo(
        f"Entries imported successfully: {stats['added']} added, {stats['updated']} updated, {stats['replaced']} replaced.")

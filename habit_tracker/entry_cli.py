import json
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
def add_entry():
    pass

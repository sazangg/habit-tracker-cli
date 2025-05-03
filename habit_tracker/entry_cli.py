import typer

app = typer.Typer(help="Manage habit entries")


@app.command("list")
def list_entries():
    pass


@app.command("add")
def add_entry():
    pass

from .entry_cli import app as entry_app
from .habit_cli import app as habit_app
import typer


app = typer.Typer()
app.add_typer(habit_app, name="habit")
app.add_typer(entry_app, name="entry")


def main():
    app()


if __name__ == "__main__":
    app()

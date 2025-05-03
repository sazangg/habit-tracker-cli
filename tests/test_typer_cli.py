import json
import os
import subprocess
import sys


def run_cli(tmp_path, *args, stdin_data: str | None = None):
    env = {
        **os.environ.copy(),
        "HABITS_PATH": str(tmp_path / "habits.json"),
        "ENTRIES_PATH": str(tmp_path / "entries.json"),
    }

    return subprocess.run(
        [sys.executable, "-m", "habit_tracker.tracker_cli", *args],
        text=True,
        input=stdin_data,
        capture_output=True,
        env=env,
        check=False
    )


def test_cli_respects_env_var(tmp_path):
    run_cli(tmp_path, "habit", "add", "pray 5 times", "-p", "4")

    data_file = tmp_path / "habits.json"
    assert data_file.exists() and data_file.stat().st_size > 0

    out = run_cli(tmp_path, "habit", "list").stdout
    assert len(json.loads(out)) == 1


def test_cli_add_and_list(tmp_path):
    rc = run_cli(tmp_path, "habit", "add", "pray 5 times", "-p", "4")
    assert rc.returncode == 0

    out = run_cli(tmp_path, "habit", "list")
    assert out.returncode == 0

    data = json.loads(out.stdout)
    assert data[0]["name"] == "pray 5 times"


def test_cli_duplicate(tmp_path):
    run_cli(tmp_path, "habit", "add", "pray")
    dup = run_cli(tmp_path, "habit", "add", "pray")
    assert dup.returncode == 1
    assert "already exists" in dup.stderr

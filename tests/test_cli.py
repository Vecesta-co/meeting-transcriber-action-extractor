import subprocess
import os
import pytest

def test_cli_info_command():
    res = subprocess.run(
        ["python", "-m", "src.cli", "info"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert "Meeting Transcriber Environment" in res.stdout
    assert "Vecesta.co" in res.stdout

def test_cli_extract_sample_fixture():
    fixture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures/sample_meeting.txt"))
    res = subprocess.run(
        ["python", "-m", "src.cli", "extract", fixture_path, "--format", "json"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0
    assert "action_items" in res.stdout
    assert "Sarah" in res.stdout


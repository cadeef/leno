# import pytest
# from devtools import debug
from typer.testing import CliRunner

from leno.cli import app

from . import fixtures

cli = CliRunner()


def test_no_command():
    """
    Ensure app runs without command, but fails
    """
    result = cli.invoke(app)
    assert result.exit_code == 2


# TODO: Parameterize for all sources
def test_update__source(tmp_path, mocker):
    """
    Verify update command
    """
    config_dir = tmp_path
    database = config_dir / "data" / "firefox.db"
    # Modify app config dir
    mocker.patch("typer.get_app_dir", return_value=config_dir)
    result = cli.invoke(app, ["update", "--source", "firefox"])
    assert database.exists()
    assert result.exit_code == 0


def test_update__list_sources():
    result = cli.invoke(app, ["update", "--list-sources"])
    assert result.exit_code == 0
    for src in fixtures.SOURCES:
        assert src in result.stdout


def test_firehose():
    pass


def test_firehose__no_token():
    result = cli.invoke(app, ["firehose"])
    assert "Missing option '--token'" in result.stdout
    assert result.exit_code == 2

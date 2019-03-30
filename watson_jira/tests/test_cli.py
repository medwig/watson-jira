import json

from click.testing import CliRunner
import pytest

from watson_jira import cli


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_logs(runner):
    result = runner.invoke(cli.main, ["logs", "--jira-only", "--tempo-format"])
    assert result.exit_code == 0
    assert isinstance(json.loads(result.output), list)


def test_tempo(runner):
    result = runner.invoke(cli.main, ["tempo", "--issue", "AP-217"])
    assert result.exit_code == 0
    assert isinstance(json.loads(result.output), list)

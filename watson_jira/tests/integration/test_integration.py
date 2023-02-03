
import json

from click.testing import CliRunner
import pytest

from watson_jira import cli


@pytest.fixture(scope="module")
def runner():
    return CliRunner()

# get card details for IntegationTest (WAT-3)
# https://medwig.atlassian.net/rest/api/3/issue/WAT-3
# delete all time tracking for WAT-3
# create new watson log for WAT-3
# sync watson logs to Jira for WAT-3
# get card details for IntegationTest (WAT-3)
# confirm that time tracking is correct for WAT-3





def test_logs(runner):
    result = runner.invoke(cli.main, ["logs"])
    assert result.exit_code == 0



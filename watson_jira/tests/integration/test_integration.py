import json
import re
from subprocess import Popen, PIPE

# from click.testing import CliRunner
import pytest

# from jira import JIRA

from watson_jira import cli

FROM = "10:00"
TO = "11:00"
PROJECT = "WAT"
TAG_ISSUE = "WAT-3"
TAG_NAME = "IntegrationTest"


class OutputParser:
    FRAME_ID_PATTERN = re.compile(r"id: (?P<frame_id>[0-9a-f]+)")

    @staticmethod
    def get_frame_id(output):
        return OutputParser.FRAME_ID_PATTERN.search(output).group("frame_id")


class WatsonHandler:
    @staticmethod
    def run(cmd):
        process = Popen(
            cmd.split(),
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, _ = process.communicate()
        return stdout.decode("ascii").strip()

    @staticmethod
    def get_test_logs():
        cmd = f"watson log -f {FROM} -t {TO} --json"
        logs = json.loads(WatsonHandler.run(cmd))
        test_logs = [
            log
            for log in logs
            if log["project"] == PROJECT
            and TAG_ISSUE in log["tags"]
            and TAG_NAME in log["tags"]
        ]
        return test_logs

    @staticmethod
    def create_test_log():
        cmd = f"watson add -f {FROM} -t {TO} {PROJECT} +{TAG_ISSUE} +{TAG_NAME}"
        WatsonHandler.run(cmd)

    @staticmethod
    def remove_test_logs():
        test_logs = WatsonHandler.get_test_logs()
        for log in test_logs:
            cmd = f"watson remove -f {log['id']}"
            WatsonHandler.run(cmd)


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


# @pytest.fixture(scope="module")
def test_init_logs():
    print("init_logs")
    WatsonHandler.create_test_log()
    test_logs = WatsonHandler.get_test_logs()
    print(test_logs)
    WatsonHandler.remove_test_logs()
    test_logs = WatsonHandler.get_test_logs()
    print(test_logs)

    # assert result.exit_code == 0
    # assert OutputParser.get_start_date(watson, result.output) == 'foo'
    return


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


if __name__ == "__main__":
    test_init_logs()

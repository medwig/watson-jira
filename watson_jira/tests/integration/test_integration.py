import json
import re
from subprocess import Popen, PIPE

# from click.testing import CliRunner
import pytest

from watson_jira import cli

from watson_jira.src import jira as jira_handler

FROM = "10:00"
TO = "11:00"
PROJECT = "WAT"
ISSUE = "WAT-3"
TAG_NAME = "IntegrationTest"


class OutputParser:
    FRAME_ID_PATTERN = re.compile(r"id: (?P<frame_id>[0-9a-f]+)")

    @staticmethod
    def get_frame_id(output):
        return OutputParser.FRAME_ID_PATTERN.search(output).group("frame_id")


class JiraHandler:
    @staticmethod
    def get_worklogs(issue, start):
        jira_handler.connect()
        worklogs = jira_handler.get_worklogs(issue)
        return worklogs

    @staticmethod
    def delete_worklog(issue, worklog_id):
        jira_handler.delete_worklog(issue, worklog_id)

    @staticmethod
    def delete_worklogs(issue, worklogs):
        for worklog in JiraHandler.get_worklogs(ISSUE, FROM):
            print(worklog)
            JiraHandler.delete_worklog(issue, worklog["id"])


def test_jira():
    worklogs = JiraHandler.get_worklogs(ISSUE, FROM)
    print(worklogs)
    JiraHandler.delete_worklogs(ISSUE, FROM)
    worklogs = JiraHandler.get_worklogs(ISSUE, FROM)
    print(worklogs)
    # for worklog in worklogs:
    #     print(worklog)
    # for worklog in worklogs:
    #     JiraHandler.delete_worklog(TAG_ISSUE, worklog["id"])
    # worklogs = JiraHandler.get_worklogs(TAG_ISSUE, FROM)
    # assert len(worklogs) == 0
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
            and ISSUE in log["tags"]
            and TAG_NAME in log["tags"]
        ]
        return test_logs

    @staticmethod
    def create_test_log():
        cmd = f"watson add -f {FROM} -t {TO} {PROJECT} +{ISSUE} +{TAG_NAME}"
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
    # test_init_logs()
    test_jira()

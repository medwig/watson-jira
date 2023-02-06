import json
import os
from subprocess import Popen, PIPE

from click.testing import CliRunner
import pytest

from watson_jira import cli

import watson_jira.src.jira

# Skip integration tests if not running on GitHub Actions
if not os.getenv('GITHUB_ACTIONS', 'False').lower() == 'true':
    pytest.skip('skipping integration tests', allow_module_level=True)

FROM = '10:00'
TO = '11:00'
TIME_SPENT = '1h'
PROJECT = 'WAT'
ISSUE = 'WAT-3'
TAG_NAME = 'IntegrationTest'


@pytest.fixture(scope='module')
def runner():
    return CliRunner()


class JiraHandler:
    @staticmethod
    def get_worklogs(issue):
        watson_jira.src.jira.connect()
        worklogs = watson_jira.src.jira.get_worklogs(issue)
        print('Worklogs: ', worklogs)
        return worklogs

    @staticmethod
    def delete_worklog(issue, worklog_id):
        watson_jira.src.jira.delete_worklog(issue, worklog_id)
        print('Worklog deleted: ', issue, worklog_id)

    @staticmethod
    def delete_worklogs(issue):
        worklogs = JiraHandler.get_worklogs(issue)
        if not worklogs:
            print('No worklogs to delete.')
            return None
        for worklog in worklogs:
            print('Deleting worklog:', issue, worklog['id'])
            JiraHandler.delete_worklog(issue, worklog['id'])
        print('Worklogs deleted.')


class WatsonHandler:
    @staticmethod
    def run(cmd):
        print('Running: ', cmd, '...')
        process = Popen(
            cmd.split(),
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, _ = process.communicate()
        return stdout.decode('ascii').strip()

    @staticmethod
    def get_test_logs():
        cmd = f'watson log -f {FROM} -t {TO} --json'
        logs = json.loads(WatsonHandler.run(cmd))
        test_logs = [
            log
            for log in logs
            if log['project'] == PROJECT
            and ISSUE in log['tags']
            and TAG_NAME in log['tags']
        ]
        print('Test logs: ', test_logs)
        return test_logs

    @staticmethod
    def create_test_log():
        cmd = f'watson add -f {FROM} -t {TO} {PROJECT} +{ISSUE} +{TAG_NAME}'
        WatsonHandler.run(cmd)

    @staticmethod
    def remove_test_logs():
        test_logs = WatsonHandler.get_test_logs()
        for log in test_logs:
            cmd = f"watson remove -f {log['id']}"
            WatsonHandler.run(cmd)
        print('Test logs removed.')


def test_sync_log_to_jira(runner):
    # create fresh test logs
    WatsonHandler.remove_test_logs()
    WatsonHandler.create_test_log()

    print('Running sync to Jira for issue ', ISSUE, '...')
    result = runner.invoke(cli.main, ['sync', '--issue', ISSUE])
    assert result.exit_code == 0

    worklogs = JiraHandler.get_worklogs(ISSUE)
    assert len(worklogs) == 1
    assert worklogs[0]['timeSpent'] == TIME_SPENT
    assert worklogs[0]['issue'] == ISSUE

    # clean up
    WatsonHandler.remove_test_logs()
    # for reasons unknown, using the cli runner here will do nothing, despite the exit code being 0
    # in fact when running *any* cli commands here, only the first will execute
    # so the library is used instead
    JiraHandler.delete_worklogs(ISSUE)

    assert WatsonHandler.get_test_logs() == []
    assert JiraHandler.get_worklogs(ISSUE) == []


if __name__ == '__main__':
    test_sync_log_to_jira()

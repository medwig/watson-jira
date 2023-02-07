import json
import os
from subprocess import Popen, PIPE

from click.testing import CliRunner
import pytest

from watson_jira import cli

from watson_jira.src import jira, watson

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
    def delete_worklogs(issue):
        worklogs = jira.get_worklogs(issue)
        for worklog in worklogs:
            print('Deleting worklog:', issue, worklog.id)
            worklog.delete()


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
        logs = json.loads(watson.run(cmd))
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
        watson.run(cmd)

    @staticmethod
    def remove_test_logs():
        test_logs = WatsonHandler.get_test_logs()
        for log in test_logs:
            cmd = f"watson remove -f {log['id']}"
            watson.run(cmd)
        print('Test logs removed.')


def test_sync_log_to_jira(runner):
    # clean slate
    WatsonHandler.remove_test_logs()
    runner.invoke(cli.main, ['delete', '--issue', ISSUE])

    # create test log
    WatsonHandler.create_test_log()

    # sync log to Jira
    print('Running sync to Jira for issue ', ISSUE, '...')
    result = runner.invoke(cli.main, ['sync', '--issue', ISSUE])
    assert result.exit_code == 0

    # download log and confirm it was synced
    result = runner.invoke(cli.main, ['tempo', '--issue', ISSUE])
    worklogs = json.loads(result.output)
    assert len(worklogs) == 1
    wl = worklogs[0]
    assert wl['timeSpent'] == TIME_SPENT
    assert wl['issue'] == ISSUE

    # clean up
    WatsonHandler.remove_test_logs()
    runner.invoke(cli.main, ['delete', '--issue', ISSUE])

    assert WatsonHandler.get_test_logs() == []
    assert jira.get_worklogs(ISSUE) == []


if __name__ == '__main__':
    test_sync_log_to_jira()

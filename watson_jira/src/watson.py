"""Watson CLI commands and Watson log handling"""

import json
from subprocess import Popen, PIPE
from datetime import datetime
from colorama import Fore

from watson_jira.src import mapper


def run(cmd):
    with Popen(
        cmd.split(),
        stdout=PIPE,
        stderr=PIPE,
    ) as process:
        stdout, stderr = process.communicate()
    return stdout.decode('ascii').strip()


def logs_to_worklogs(logs, is_interactive):
    """Convert Watson logs to Tempo (Jira) worklog dictionaries"""
    print(Fore.YELLOW + 'Mapping watson logs to JIRA tickets')
    worklogs = []
    for log in logs:
        jira_issue = mapper.map(log['project'], log['tags'], is_interactive)
        if jira_issue is None:
            continue

        worklog = {
            'started': log['start'],
            'issue': jira_issue,
            'comment': get_comment(log['id'], log['project'], log['tags']),
            'timeSpent': get_time_spent(log['start'], log['stop']),
        }
        worklogs.append(worklog)
    return worklogs


def get_comment(id, project, tags):
    return '{0}\n{1} - [{2}]'.format(id, project, ', '.join(tags))


def get_time_spent(start, stop):
    datetime_start = datetime.fromisoformat(start)
    datetime_stop = datetime.fromisoformat(stop)
    return int((datetime_stop - datetime_start).total_seconds() // 60 or 1)


def log_day(date, tempo_format=False, is_interactive=False):
    """Get Watson logs for given date in JSON"""
    cmd = f'watson log --from {date} --to {date} --json'
    logs = json.loads(run(cmd))
    if tempo_format:
        logs = logs_to_worklogs(logs, is_interactive)
    return logs

import json

import click
import simplejson

from src import watson
from src import jira

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def greet():
    pass

@greet.command()
@click.option('--issue', default=None, help='get worklogs from this issue')
@click.option('--id', default=None, help='get specific worklog by id')
# @click.option('--tempo-format', is_flag=True, help='format logs for tempo timesheet')
def tempo(**kwargs):
    issue = kwargs['issue']
    _id = kwargs['id']
    if _id:
        worklogs = jira.get_worklog(issue, _id)
    else:
        worklogs = jira.get_worklogs(issue)

    print(simplejson.dumps(worklogs, skipkeys=True))


@greet.command()
@click.option('--date', default='None', help='date to get logs')
@click.option('--jira-only', is_flag=True, help='only return logs for Jira issues')
@click.option('--tempo-format', is_flag=True, help='format logs for tempo timesheet')
def logs(**kwargs):
    date = kwargs['date']
    jira_only = kwargs['jira_only']
    logs = watson.report_day(date, jira_only)

    if kwargs['tempo_format']:
        logs = watson.report_to_worklogs(logs)

    print(json.dumps(logs))

if __name__ == '__main__':
    greet()
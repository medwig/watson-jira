import json
from datetime import datetime
from dateutil.parser import parse

import click
import simplejson

from src import watson
from src import jira

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def get_logs(date, jira_only=False, tempo_format=False):
    logs = watson.report_day(date, jira_only)
    if tempo_format:
        logs = watson.report_to_worklogs(logs)
    return logs


def to_ymd(datestring):
    return datestring.split('T')[0]


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def greet():
    pass


@greet.command()
@click.option('--date', default='None', help='date to sync logs')
@click.option('--issue', default=None, help='only sync logs for this issue')
def sync(**kwargs):
    date = kwargs['date']
    issue = kwargs['issue']
    logs = get_logs(date, jira_only=True, tempo_format=True)
    if issue:
        logs = [l for l in logs if l['issue'] == issue] 

    for log in logs:
        worklogs = jira.get_worklogs(log['issue'])
        if any([log['comment'] == wl['comment'] for wl in worklogs]):
            # Log already exists in Jira worklogs
            print('Log already exists')
        else:
            # Log does not exist in Jira, upload
            print('syncing log')
            jira.add_worklog(**log)
        print('-'*20)


@greet.command()
@click.option('--issue', default=None, help='get worklogs from this issue')
@click.option('--id', default=None, help='get specific worklog by id')
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
    tempo_format = kwargs['tempo_format']

    logs = get_logs(date, jira_only, tempo_format)
    print(json.dumps(logs))

if __name__ == '__main__':
    greet()
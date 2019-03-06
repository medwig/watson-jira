import json

import click

from src import watson

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def greet():
    pass


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
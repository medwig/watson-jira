"""Click CLI interface"""

import json
from datetime import date

import colorama
import click
import simplejson
from colorama import Fore
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from dateutil.parser import parse

from watson_jira.src import watson, jira, config

colorama.init(autoreset=True)

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}
TODAY = date.today()
TODAY_YMD = TODAY.strftime('%Y-%m-%d')

# colors
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
RESET = Fore.RESET
GREEN = Fore.GREEN
RED = Fore.RED
LIGHTBLACK_EX = Fore.LIGHTBLACK_EX
CYAN = Fore.CYAN


def to_ymd(datestring):
    return datestring.split('T')[0]


def dates_from(days_ago):
    dates = rrule(
        DAILY, dtstart=TODAY - relativedelta(days=days_ago), until=TODAY
    )
    return [d.strftime('%Y-%m-%d') for d in dates]


def sync_logs(logs):
    if not logs:
        click.echo('No logs')
    else:
        click.echo(f'\n{YELLOW}Syncing to JIRA')

    for log in logs:
        started_datetime = parse(log['started'])
        started_formatted = started_datetime.strftime('%H:%M')
        click.echo(
            f"{BLUE}{log['issue']}{RESET} at {GREEN}{started_formatted}{RESET} {log['timeSpent']}m ",
            nl=False,
        )

        worklogs = jira.get_worklogs(log['issue'])
        if any(
            (
                log['comment'] == wl.comment
                and started_datetime.date() == parse(wl.started).date()
                for wl in worklogs
            )
        ):
            click.echo(f'{YELLOW}already exists')
        else:
            jira.add_worklog(**log)
            click.echo(f'{GREEN}synced')


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def main():
    pass


@main.command()
@click.option('--date', default=None, help='date to sync logs')
@click.option(
    '--from', default=0, type=int, help='sync logs from this many days ago'
)
@click.option('--issue', default=None, help='only sync logs for this issue')
@click.option(
    '--interactive',
    is_flag=True,
    help='enable prompts to confirm or change target issue',
)
def sync(**kwargs):
    days_ago = kwargs['from']
    date = kwargs['date']
    issue = kwargs['issue']
    is_interactive = kwargs['interactive']

    datelist = dates_from(days_ago)
    if date:  # specific date trumps a range
        datelist = [date]

    for date in datelist:
        click.echo(f'\n{CYAN}{date}')
        logs = watson.log_day(
            date, tempo_format=True, is_interactive=is_interactive
        )
        if issue:
            logs = [l for l in logs if l['issue'] == issue]

        sync_logs(logs)

    click.echo(f'\n{CYAN}Synchronization finished{RESET}\n')


@main.command()
@click.option(
    '--issue',
    required=True,
    help='issue to delete worklogs from (on Jira server only)',
)
@click.option(
    '--interactive',
    is_flag=True,
    help='enable propmts to delete worklogs for target issue',
)
def delete(**kwargs):
    issue = kwargs['issue']
    is_interactive = kwargs['interactive']

    worklogs = jira.get_worklogs(issue)
    click.echo(
        f'\n{YELLOW}Deleting {len(worklogs)} worklogs from Jira issue {issue}'
    )
    for worklog in worklogs:
        if is_interactive:
            click.echo(
                f'Delete worklog {worklog.id} from {worklog.started} for {worklog.timeSpent}?'
            )
            if click.confirm('Continue?'):
                worklog.delete()
            else:
                click.echo('Skipping')
        else:
            worklog.delete()

    click.echo(f'\n{CYAN}Deletion Finished{RESET}\n')


@main.command()
@click.option(
    '--issue',
    default=None,
    required=True,
    help='get Jira worklogs for this issue',
)
@click.option('--id', default=None, help='get specific worklog by id')
def tempo(**kwargs):
    issue = kwargs['issue']
    _id = kwargs['id']
    if _id:
        output = jira.get_worklog(issue, _id, as_dict=True)
    else:
        output = jira.get_worklogs(issue, as_dict=True)
    click.echo(simplejson.dumps(output, skipkeys=True))


@main.command()
@click.option('--date', default=TODAY_YMD, help='date to get Watson logs')
@click.option(
    '--tempo-format', is_flag=True, help='format logs for tempo (Jira format)'
)
def logs(**kwargs):
    logs = watson.log_day(kwargs['date'], kwargs['tempo_format'])
    click.echo(json.dumps(logs))


@main.command()
@click.option(
    '--clean-existing', is_flag=True, help='override existing config'
)
@click.option(
    '--show-config', is_flag=True, help='show current config file and exit'
)
def init(**kwargs):
    if kwargs['show_config']:
        current_config = config.load_config()
        click.echo(json.dumps(current_config))
        return

    if not kwargs['clean_existing'] and jira.get_user():
        click.echo(f'\n{GREEN}done')
        return

    data = {}
    data['jira'] = {}
    data['jira']['server'] = click.prompt(BLUE + 'Jira server URL', type=str)

    auth_method = click.prompt(
        f"""{BLUE}Jira authentication method
  {RESET}0 {LIGHTBLACK_EX}={BLUE} Personal access token
  {RESET}1 {LIGHTBLACK_EX}={BLUE} Email and Api token
  {RESET}2 {LIGHTBLACK_EX}={BLUE} Cookie
Your selection{RESET}""",
        type=int,
        default='0',
    )

    if auth_method == 0:
        data['jira']['personalAccessToken'] = click.prompt(
            f'{BLUE}Personal access token', type=str
        )
    elif auth_method == 1:
        data['jira']['email'] = click.prompt(BLUE + 'Jira email', type=str)
        click.echo(
            f'{LIGHTBLACK_EX}Create token at https://id.atlassian.com/manage/api-tokens#'
        )
        data['jira']['apiToken'] = click.prompt(f'{BLUE}Api token', type=str)
    elif auth_method == 2:
        click.echo(
            f"{LIGHTBLACK_EX}In browser open developer tools and Network tab.\nIf no request is visible, then refresh page.\nOpen details of any GET request, and copy 'Cookie' from the Request Headers section.\nIt's ok to paste also with 'Cookie: ' field name."
        )
        cookie = click.prompt(f'{BLUE}Cookie', type=str)
        if cookie.startswith('Cookie: '):
            cookie = cookie[cookie.find(' ') + 1 :]
        data['jira']['cookie'] = cookie
    else:
        click.echo(f'{RED}Invalid value')
        return

    data['mappings'] = []

    config.set_config(data)

    current_user = jira.get_user()
    if not current_user:
        click.echo(
            f"{RED}Unable to fetch user's Jira display name with provided configuration!"
        )
    click.echo(GREEN + f'Connected as {current_user}')


if __name__ == '__main__':
    main()

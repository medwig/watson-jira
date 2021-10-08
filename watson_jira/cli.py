import os
import json
from datetime import date

import colorama
import click
import simplejson
from colorama import Fore, Style
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from dateutil.parser import parse

from watson_jira.src import watson, jira, config

colorama.init(autoreset=True)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
TODAY = date.today()
TODAY_YMD = TODAY.strftime("%Y-%m-%d")


def to_ymd(datestring):
    return datestring.split("T")[0]


def dates_from(days_ago):
    dates = rrule(DAILY, dtstart=TODAY - relativedelta(days=days_ago), until=TODAY)
    return [d.strftime("%Y-%m-%d") for d in dates]


def sync_logs(logs):
    if not logs:
        print("No logs")
    else:
        print(Fore.YELLOW + "\nSyncing to JIRA")

    for log in logs:
        started_datetime = parse(log["started"])
        started_formatted = started_datetime.strftime("%H:%M")
        print(
            f"{Fore.BLUE}{log['issue']}{Fore.RESET} at {Fore.GREEN}{started_formatted}{Fore.RESET} {log['timeSpent']}m ",
            end="",
        )

        worklogs = jira.get_worklogs(log["issue"])
        if any(
            [
                log["comment"] == wl["comment"]
                and started_datetime.date() == parse(wl["started"]).date()
                for wl in worklogs
            ]
        ):
            print(Fore.YELLOW + "already exists")
        else:
            # jira.add_worklog(**log)
            print(Fore.GREEN + "synced")

    return True


def jira_connect():
    try:
        jira.connect()
        return True
    except config.ConfigException as e:
        click.echo(Fore.RED + f"Configuration error: {e}")
    except jira.JiraException as e:
        click.echo(Fore.RED + f"JIRA error: {e}")

    return False


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0")
def main():
    pass


@main.command()
@click.option("--date", default=None, help="date to sync logs")
@click.option("--from", default=0, type=int, help="sync logs from this long ago")
@click.option("--issue", default=None, help="only sync logs for this issue")
@click.option(
    "--interactive",
    is_flag=True,
    help="enable propmts to confirm or change target issue",
)
def sync(**kwargs):
    if jira_connect():
        days_ago = kwargs["from"]
        date = kwargs["date"]
        issue = kwargs["issue"]
        is_interactive = kwargs["interactive"]

        datelist = dates_from(days_ago)
        if date:  # specific date trumps a range
            datelist = [date]

        for date in datelist:
            print()
            print(Fore.CYAN + Style.NORMAL + f"{date}")
            logs = watson.log_day(
                date, tempo_format=True, is_interactive=is_interactive
            )
            if issue:
                logs = [l for l in logs if l["issue"] == issue]

            sync_logs(logs)

        print(Fore.CYAN + "\nSynchronization finished\n" + Fore.RESET)


@main.command()
@click.option(
    "--issue", default=None, required=True, help="get worklogs from this issue"
)
@click.option("--id", default=None, help="get specific worklog by id")
def tempo(**kwargs):
    if jira_connect():
        issue = kwargs["issue"]
        _id = kwargs["id"]
        if _id:
            worklogs = jira.get_worklog(issue, _id)
        else:
            worklogs = jira.get_worklogs(issue)
        click.echo(simplejson.dumps(worklogs, skipkeys=True))


@main.command()
@click.option("--date", default=TODAY_YMD, help="date to get logs")
@click.option("--tempo-format", is_flag=True, help="format logs for tempo timesheet")
def logs(**kwargs):
    logs = watson.log_day(kwargs["date"], kwargs["tempo_format"])
    click.echo(json.dumps(logs))


# TODO: rewrite to init at least config
@main.command()
def init(**kwargs):
    current_user = jira.test_conn()
    if current_user:
        click.echo(f'Configured as user="{current_user}" and ready to go!')
        return
    print(
        "create token here and copy to clipboard:\n>> https://id.atlassian.com/manage/api-tokens#\n"
    )
    token = click.prompt("Jira token: ", type=str)
    email = click.prompt("Jira email: ", type=str)
    url = click.prompt("Jira url (example fooco.atlassian.net): ", type=str)
    with open(os.path.expanduser("~/.config/watson-jira/.netrc"), "a+") as netrc:
        netrc.writelines(
            ["\n" f"machine {url}\n" f"login {email}\n" f"password {token}\n"]
        )
    click.echo(Fore.YELLOW + "\n~\\.netrc written\nReady to go!")


if __name__ == "__main__":
    main()

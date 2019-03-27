import json
from datetime import datetime, date

import click
import simplejson
import colorama
from colorama import Fore, Style
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY

from src import watson
from src import jira

colorama.init(autoreset=True)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
TODAY = date.today()


def get_logs(date, jira_only=False, tempo_format=False):
    logs = watson.report_day(date, jira_only)
    if tempo_format:
        logs = watson.report_to_worklogs(logs)
    return logs


def to_ymd(datestring):
    return datestring.split("T")[0]


def dates(days_ago):
    dates = rrule(DAILY, dtstart=TODAY - relativedelta(days=days_ago), until=TODAY)
    return [d.strftime("%Y-%m-%d") for d in dates]


def sync_logs(logs):
    if not logs:
        print("No logs")
    for log in logs:
        worklogs = jira.get_worklogs(log["issue"])
        print(
            Fore.YELLOW
            + Style.NORMAL
            + f"{log['issue']}, {log['timeSpent']}, {log['comment']}"
        )
        if any([log["comment"] == wl["comment"] for wl in worklogs]):
            print("Log already exists")
        else:
            jira.add_worklog(**log)
            print("synced log")
        print()
    return True


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version="1.0.0")
def greet():
    pass


@greet.command()
@click.option("--date", default=None, help="date to sync logs")
@click.option("--from", default=0, type=int, help="sync logs from this long ago")
@click.option("--issue", default=None, help="only sync logs for this issue")
def sync(**kwargs):
    from_days = kwargs["from"]
    date = kwargs["date"]
    issue = kwargs["issue"]

    datelist = dates(from_days)
    if date:  # specific date trumps a range
        datelist = [date]

    for date in datelist:
        print(Fore.GREEN + Style.NORMAL + f"{date}")
        logs = get_logs(date, jira_only=True, tempo_format=True)
        if issue:
            logs = [l for l in logs if l["issue"] == issue]
        sync_logs(logs)
        print("-" * 20)


@greet.command()
@click.option("--issue", default=None, help="get worklogs from this issue")
@click.option("--id", default=None, help="get specific worklog by id")
def tempo(**kwargs):
    issue = kwargs["issue"]
    _id = kwargs["id"]
    if _id:
        worklogs = jira.get_worklog(issue, _id)
    else:
        worklogs = jira.get_worklogs(issue)

    print(simplejson.dumps(worklogs, skipkeys=True))


@greet.command()
@click.option("--date", default="None", help="date to get logs")
@click.option("--jira-only", is_flag=True, help="only return logs for Jira issues")
@click.option("--tempo-format", is_flag=True, help="format logs for tempo timesheet")
def logs(**kwargs):
    date = kwargs["date"]
    jira_only = kwargs["jira_only"]
    tempo_format = kwargs["tempo_format"]

    logs = get_logs(date, jira_only, tempo_format)
    print(json.dumps(logs))


if __name__ == "__main__":
    greet()

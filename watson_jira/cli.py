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
            jira.add_worklog(**log)
            print(Fore.GREEN + "synced")

    return True


def jira_connect():
    try:
        connection_info = jira.connect()
        if connection_info:
            (server, auth_method) = connection_info
            print(f"Connecting to {server}")
            if auth_method == "pat":
                print("Using personal access token auth method")
            elif auth_method == "apiToken":
                print("Using email with API token auth method")
            else:
                print("Using cookie auth method")

            return True
    except config.ConfigException as e:
        click.echo(Fore.RED + f"Configuration error: {e}")
        click.echo(Fore.LIGHTBLACK_EX + "You can try to run 'watson-jira init'")
    except jira.JiraException as e:
        click.echo(Fore.RED + f"JIRA error: {e}")

    return False


def check_connection():
    try:
        jira.connect()
        current_user = jira.test_conn()
        if current_user:
            click.echo(Fore.GREEN + f"Connected as {current_user}")
            click.echo(
                Fore.LIGHTBLACK_EX
                + f"Please make sure to define mappings in the config file (default in ~/.config/watson-jira/)"
            )
            return True
    except Exception:
        pass
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
@click.argument("issue")
@click.option(
    "--interactive",
    is_flag=True,
    help="enable propmts to delete worklogs for target issue",
)
def delete(**kwargs):
    if jira_connect():
        issue = kwargs["issue"]
        is_interactive = kwargs["interactive"]

        worklogs = jira.get_worklogs(issue)
        print(Fore.YELLOW + f"\nDeleting {len(worklogs)} worklogs from Jira issue {issue}")
        for wl in worklogs:
            if is_interactive:
                click.echo(
                    f"Delete worklog {wl['id']} from {wl['started']} for {wl['timeSpent']}?"
                )
                if click.confirm("Continue?"):
                    jira.delete_worklog(issue, wl["id"])
                else:
                    click.echo("Skipping")
            else:
                jira.delete_worklog(issue, wl["id"])

        print(Fore.CYAN + "\nDeletion Finished \n" + Fore.RESET)


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


@main.command()
@click.option("--clean-existing", is_flag=True, help="override existing config")
def init(**kwargs):
    if not kwargs["clean_existing"] and check_connection():
        return

    data = {}
    data["jira"] = {}
    data["jira"]["server"] = click.prompt(Fore.BLUE + "Jira server URL", type=str)

    auth_method = click.prompt(
        f"""{Fore.BLUE}Jira authentication method
  {Fore.RESET}0 {Fore.LIGHTBLACK_EX}={Fore.BLUE} Personal access token
  {Fore.RESET}1 {Fore.LIGHTBLACK_EX}={Fore.BLUE} Email and Api token
  {Fore.RESET}2 {Fore.LIGHTBLACK_EX}={Fore.BLUE} Cookie
Your selection{Fore.RESET}""",
        type=int,
        default="0",
    )

    if auth_method == 0:
        data["jira"]["personalAccessToken"] = click.prompt(
            Fore.BLUE + "Personal access token", type=str
        )
    elif auth_method == 1:
        data["jira"]["email"] = click.prompt(Fore.BLUE + "Jira email", type=str)
        click.echo(
            Fore.LIGHTBLACK_EX
            + "Create token at https://id.atlassian.com/manage/api-tokens#"
        )
        data["jira"]["apiToken"] = click.prompt(Fore.BLUE + "Api token", type=str)
    elif auth_method == 2:
        click.echo(
            Fore.LIGHTBLACK_EX
            + "In browser open developer tools and Network tab.\nIf no request is visible, then refresh page.\nOpen details of any GET request, and copy 'Cookie' from the Request Headers section.\nIt's ok to paste also with 'Cookie: ' field name."
        )
        cookie = click.prompt(Fore.BLUE + "Cookie", type=str)
        if cookie.startswith("Cookie: "):
            cookie = cookie[cookie.find(" ") + 1 :]
        data["jira"]["cookie"] = cookie
    else:
        click.echo(Fore.RED + f"Invalid value")
        return

    data["mappings"] = []

    config.set(data)
    jira.invalidate()

    if not check_connection():
        click.echo(
            Fore.RED
            + "Unable to fetch user's display name with provided configuration!"
        )


if __name__ == "__main__":
    main()

import json
from subprocess import Popen, PIPE
from datetime import datetime

from watson_jira.src import mapper


def filter_jiras(report):
    jira_projects = []
    for project in report["projects"]:
        if mapper.is_jira_issue(project["name"]):
            jira_projects.append(project)
    report["projects"] = jira_projects
    return report


# TODO: make it work with the mapper
def report_to_worklogs(report):
    """Convert watson report to Tempo (Jira) worklog dictionaries"""
    date = report["timespan"]["to"]
    worklogs = []
    for project in report["projects"]:
        for tag in project["tags"]:
            worklog = {
                "issue": project["name"],
                "started": date,
                "comment": tag["name"],
                "timeSpent": int(
                    tag["time"] // 60 or 1
                ),  # Watson logs in seconds, Jira in minutes
            }
            worklogs.append(worklog)
    report["projects"] = worklogs
    return report


def logs_to_worklogs(logs):
    """Convert Watson logs to Tempo (Jira) worklog dictionaries"""
    worklogs = []
    for log in logs:
        jira_issue = mapper.map(log["project"], log["tags"])
        if jira_issue is None:
            continue

        worklog = {
            "started": log["start"],
            "issue": jira_issue,
            "comment": get_comment(log["id"], log["project"], log["tags"]),
            "timeSpent": get_time_spent(log["start"], log["stop"]),
        }
        worklogs.append(worklog)
    return worklogs


def get_comment(id, project, tags):
    return "{0}\n{1} - [{2}]".format(id, project, ", ".join(tags))


def get_time_spent(start, stop):
    datetime_start = datetime.fromisoformat(start)
    datetime_stop = datetime.fromisoformat(stop)
    return int((datetime_stop - datetime_start).total_seconds() // 60 or 1)


def report_day(date, jira_only=False, tempo_format=False):
    """Get Watson report for a given date in JSON"""
    process = Popen(
        ["watson", "report", "--from", date, "--to", date, "--json"],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, _stderr = process.communicate()
    report = json.loads(stdout.decode("ascii").strip())
    if jira_only:
        report = filter_jiras(report)
    if tempo_format:
        report = report_to_worklogs(report)
    return report["projects"]


def log_day(date, tempo_format=False):
    """Get Watson logs for given date in JSON"""
    process = Popen(
        ["watson", "log", "--from", date, "--to", date, "--json"],
        stdout=PIPE,
        stderr=PIPE,
    )
    stdout, _stderr = process.communicate()
    logs = json.loads(stdout.decode("ascii").strip())
    if tempo_format:
        logs = logs_to_worklogs(logs)
    return logs

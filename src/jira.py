from datetime import datetime
from dateutil.parser import parse
import json

from jira import JIRA


# credentials are stored in ~/.netrc
jira = JIRA({"server": "https://skywatch.atlassian.net"})


def get_worklog(issue, _id):
    worklog = jira.worklog(issue, _id)
    return vars(worklog)


def get_worklogs(issue):
    worklogs = jira.worklogs(issue)
    parsed_worklogs = []
    for worklog in worklogs:
        wl = {
            "issue": issue,
            "comment": worklog.comment,
            "started": worklog.started,
            "timeSpent": worklog.timeSpent,
            "id": worklog.id,
        }
        parsed_worklogs.append(wl)
    return parsed_worklogs


def add_worklog(issue, timeSpent, comment, started):
    wl = jira.add_worklog(
        issue, timeSpent=timeSpent, comment=comment, started=parse(started)
    )
    return wl


def worklog_exists_in_jira(local_worklog):
    jira_worklogs = get_worklogs(worklog.issue)
    date = parser(local_worklog["started"])


def add_all_worklogs(worklogs):
    """Adds all worklogs to JIRA, excluding those that already exist"""
    # For each worklog
    for local_worklog in worklogs:
        # Check if wl exits in JIRA
        if worklog_exists_in_jira(local_worklog):
            # If yes, log that and skip
            print("worklog exists in JIRA!")
            continue
        # If no, add_wl and log that
        print("stubbed add_worklog cmd")


if __name__ == "__main__":
    issue = "OO-642"
    time_spent = "1.5m"
    comment = "comment_test_test"
    started = datetime(2006, 11, 21, 16, 30)
    wls = get_worklogs(issue)
    #print(json.dumps(wls))
    #  r = add_worklog(issue, time_spent, comment, started)
    #  print(r)

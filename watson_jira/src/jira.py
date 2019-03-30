from dateutil.parser import parse

from jira import JIRA


# credentials are stored in ~/.netrc
jira = JIRA("https://skywatch.atlassian.net")


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


if __name__ == "__main__":
    pass

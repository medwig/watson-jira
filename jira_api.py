from pprint import pprint
from datetime import datetime
from jira import JIRA


# credentials are stored in ~/.netrc
jira = JIRA({'server': 'https://skywatch.atlassian.net'})

issue = 'OO-762'
time_spent = '1.5m'
comment = 'comment_test_test'
started = datetime(2006, 11, 21, 16, 30)


def get_worklogs(issue):
    issue = jira.issue(issue)
    worklogs = issue.fields.worklog.worklogs
    for worklog in worklogs:
        print(worklog.started, worklog.timeSpent, worklog.comment)
    return worklogs


def add_worklog(issue, time_spent, comment, started):
    wl = jira.add_worklog(
        issue,
        timeSpent=time_spent,
        comment=comment,
        started=started
    )
    return wl


if __name__ == '__main__':
    get_worklogs(issue)

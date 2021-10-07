from dateutil.parser import parse
from watson_jira.src import config

jira = config.prepare_jira_connection()

def get_worklog(issue, _id):
    worklog = jira.worklog(issue, _id)
    return vars(worklog)


def get_worklogs(issue):
    worklogs = jira.worklogs(issue)
    parsed_worklogs = []
    for worklog in worklogs:
        wl = {
            "issue": issue,
            "comment": worklog.comment if hasattr(worklog, 'comment') else None,
            "started": worklog.started,
            "timeSpent": worklog.timeSpent,
            "id": worklog.id,
        }
        parsed_worklogs.append(wl)
    return parsed_worklogs


def add_worklog(issue, timeSpent, comment, started):
    print(f"issue = {issue}, timeSpent={timeSpent}, comment={comment}, started={started}")
    wl = jira.add_worklog(
        issue, timeSpent=timeSpent, comment=comment, started=parse(started)
    )
    return wl


def test_conn():
    user = jira.current_user()
    try:
        assert user != "anonymous"
    except AssertionError:
        return False
    return user


if __name__ == "__main__":
    pass

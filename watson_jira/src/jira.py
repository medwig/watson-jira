from dateutil.parser import parse
from watson_jira.src import config
from jira import JIRA
from typing import Optional

jira: Optional[JIRA] = None


class JiraException(Exception):
    pass


def invalidate():
    global jira
    jira = None


def connect():
    global jira
    if jira is None:
        jiraconfig = config.jira()
        try:
            if jiraconfig["pat"]:
                auth_method = "pat"
                headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
                headers["Authorization"] = jiraconfig["pat"]
                jira = JIRA(server=jiraconfig["server"], options={"headers": headers})

            elif jiraconfig["apiToken"]:
                auth_method = "apiToken"
                auth = (jiraconfig["email"], jiraconfig["apiToken"])
                jira = JIRA(server=jiraconfig["server"], basic_auth=auth)

            else:
                auth_method = "cookie"
                headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
                headers["cookie"] = jiraconfig["cookie"]
                jira = JIRA(server=jiraconfig["server"], options={"headers": headers})

            return (jiraconfig["server"], auth_method)
        except Exception:
            raise JiraException("Connection failed")


def get_worklog(issue, _id):
    global jira
    if jira is None:
        raise JiraException("Jira not connected")
    worklog = jira.worklog(issue, _id)
    return vars(worklog)


def get_worklogs(issue):
    global jira
    if jira is None:
        raise JiraException("Jira not connected")
    worklogs = jira.worklogs(issue)
    parsed_worklogs = []
    for worklog in worklogs:
        wl = {
            "issue": issue,
            "comment": worklog.comment if hasattr(worklog, "comment") else None,
            "started": worklog.started,
            "timeSpent": worklog.timeSpent,
            "id": worklog.id,
        }
        parsed_worklogs.append(wl)
    return parsed_worklogs


def add_worklog(issue, timeSpent, comment, started):
    global jira
    if jira is None:
        raise JiraException("Jira not connected")
    wl = jira.add_worklog(
        issue, timeSpent=timeSpent, comment=comment, started=parse(started)
    )
    return wl


def test_conn():
    global jira
    if jira is None:
        raise JiraException("Jira not connected")
    user = jira.current_user("displayName")
    try:
        assert user != "anonymous"
    except AssertionError:
        return False
    return user


if __name__ == "__main__":
    pass

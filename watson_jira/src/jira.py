"""Jira API connection and worklog handling"""

from dateutil.parser import parse

from jira import JIRA

from watson_jira.src import config


class JiraException(Exception):
    pass


def connect():
    jiraconfig = config.jira()
    try:
        if jiraconfig['pat']:
            headers = JIRA.DEFAULT_OPTIONS['headers'].copy()
            headers['Authorization'] = jiraconfig['pat']
            jira = JIRA(
                server=jiraconfig['server'], options={'headers': headers}
            )

        elif jiraconfig['apiToken']:
            auth = (jiraconfig['email'], jiraconfig['apiToken'])
            jira = JIRA(server=jiraconfig['server'], basic_auth=auth)

        else:
            headers = JIRA.DEFAULT_OPTIONS['headers'].copy()
            headers['cookie'] = jiraconfig['cookie']
            jira = JIRA(
                server=jiraconfig['server'], options={'headers': headers}
            )

        return jira
    except Exception as exc:
        raise JiraException('Connection failed') from exc


def worklog_to_dict(worklog, issue):
    return {
        'issue': issue,
        'comment': getattr(worklog, 'comment', None),
        'started': worklog.started,
        'timeSpent': worklog.timeSpent,
        'id': worklog.id,
    }


def get_worklog(issue, _id, as_dict=False):
    jira_conn = connect()
    worklog = jira_conn.worklog(issue, _id)
    if as_dict:
        worklog_to_dict(worklog, issue)
    return worklog


def get_worklogs(issue, as_dict=False):
    jira_conn = connect()
    worklogs = jira_conn.worklogs(issue)
    if as_dict:
        return [worklog_to_dict(worklog, issue) for worklog in worklogs]
    return worklogs


def add_worklog(issue, time_spent, comment, started):
    jira_conn = connect()
    worklog = jira_conn.add_worklog(
        issue, timeSpent=time_spent, comment=comment, started=parse(started)
    )
    return worklog


def get_user():
    jira_conn = connect()
    user = jira_conn.current_user('displayName')
    if user == 'anonymous':
        return False
    return user


if __name__ == '__main__':
    pass

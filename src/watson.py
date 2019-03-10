import json
import re
from subprocess import Popen, PIPE


def is_jira_issue(string):
    """Returns True if input string is a valid JIRA issue key, else False"""
    jira_regex = r'^[A-Z]{1,10}-[0-9]+$'
    return bool(re.match(jira_regex, string))


def filter_jiras(report):
    jira_projects = []
    for project in report['projects']:
        if is_jira_issue(project['name']):
            jira_projects.append(project)
    report['projects'] = jira_projects
    return report


def report_to_worklogs(report):
    """Convert watson report to Tempo (Jira) worklog dictionaries"""
    date = report['timespan']['to']
    worklogs = []
    for project in report['projects']:
        for tag in project['tags']:
            worklog = {
                'issue': project['name'],
                'started': date,
                'comment': tag['name'],
                'timeSpent': int(tag['time'] // 60 or 1)  # Watson logs in seconds, Jira in minutes
            }
            worklogs.append(worklog)
    return worklogs


def report_day(date, jira_only=False):
    """Get Watson report for a given date in JSON"""
    process = Popen(['watson', 'report', '--from', date, '--to', date,
                     '--json'], stdout=PIPE, stderr=PIPE)
    # cmd = process.args
    stdout, stderr = process.communicate()
    report = json.loads(stdout.decode('ascii').strip())
    if jira_only:
        report = filter_jiras(report) 
    return report

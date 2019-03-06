# Parser - reads a Watson json report and prints a worklog report
import json
import re
import datetime
import pprint
from subprocess import Popen, PIPE
import argparse


def is_jira_issue(string):
    """Returns True if input string is a valid JIRA issue key, else False"""
    jira_regex = r'^[A-Z]{1,10}-[0-9]+$'
    return bool(re.match(jira_regex, string))


def report_to_worklogs(report):
    """Convert watson report to JIRA worklog dictionaries"""
    date = report['timespan']['from']

    worklogs = []
    for project in report['projects']:
        if is_jira_issue(project['name']):
            for tag in project['tags']:
                worklog = {
                    'issue': project['name'],
                    'started': date,
                    'comment': tag['name'],
                    'timeSpent': tag['time']
                }
                worklogs.append(worklog)
    return worklogs


def report_day(date):
    """Get Watson report for a given date in JSON"""
    process = Popen(['watson', 'report', '--from', date, '--to', date,
                     '--json'], stdout=PIPE, stderr=PIPE)
    # cmd = process.args
    stdout, stderr = process.communicate()
    report = json.loads(stdout.decode('ascii').strip())
    return report


if __name__ == '__main__':
    TODAY = datetime.datetime.today().strftime('%Y-%m-%d')
    parser = argparse.ArgumentParser(description='Process a watson report.')
    parser.add_argument('date', type=str, default=TODAY, nargs='?', help='the date to report for')
    args = parser.parse_args()
    print('date = {}'.format(args.date))

    report = report_day(args.date)
    pprint.pprint(report)
    worklogs = report_to_worklogs(report)
    pprint.pprint(worklogs)

# Parser - reads a Watson json report and prints a worklog report
import json
import re
from dateutil import parser


def is_jira_issue(string):
    """Returns True if input string is a valid JIRA issue key, else False"""
    jira_regex = r'^[A-Z]{1,10}-[0-9]+$'
    return bool(re.match(jira_regex, string))


def delta_seconds(start, stop):
    """Calculate time delta /w 2 date strings form 2018-11-29T17:10:06-05:00"""
    delta = parser.parse(stop) - parser.parse(start)
    return delta.seconds


def parse_frames(frames_str):
    """Convert jira frame dictionaries to JIRA worklog dictionaries"""
    worklogs = []
    frames = json.loads(frames_str)
    for frame in frames:
        if not is_jira_issue(frame['project']):
            continue
        worklog = {
            'issue': frame['project'],
            'comment': ', '.join(frame['tags']),
            'started': frame['start'],
            'timeSpent': delta_seconds(frame['start'], frame['stop'])
        }
        worklogs.append(worklog)
    return worklogs


if __name__ == '__main__':
    with open('watson_log.json', 'r') as f:
        was_log = f.read()
    worklogs = parse_frames(was_log)
    for w in worklogs:
        print(w)

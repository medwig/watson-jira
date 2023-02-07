"""Maps Watson project and tags to JIRA issue key"""

import re
import click
from colorama import Fore

from watson_jira.src import config

# colors
BLUE = Fore.BLUE
RESET = Fore.RESET
GREEN = Fore.GREEN
RED = Fore.RED
MAGENTA = Fore.MAGENTA


def is_jira_issue(string):
    """Returns True if input string is a valid JIRA issue key, else False"""
    jira_regex = r'^[A-Z]{1,10}-[0-9]+$'
    return bool(re.match(jira_regex, string))


def process_single_issue(mapping):
    return mapping['issue']


def process_issue_per_project(mapping, project):
    if project in mapping['projects'].keys():
        return mapping['projects'][project]
    return None


def process_issue_specified_in_tag(tags):
    for tag in tags:
        if is_jira_issue(tag):
            return tag
    return None


def ask():
    return click.prompt('Specify jira issue (leave empty to skip)', default='')


def map_issue(project, tags, is_interactive):
    mappings = config.mappings()

    # resolve jira issue from the tag
    jira_issue = None
    for mapping in mappings:
        if mapping['name'] in tags:
            if mapping['type'] == 'single_issue':
                jira_issue = process_single_issue(mapping)
            elif mapping['type'] == 'issue_per_project':
                jira_issue = process_issue_per_project(mapping, project)
        else:   # default to issue_specified_in_tag
            jira_issue = process_issue_specified_in_tag(tags)

    # backward compatibility - resolve jira issue from project name
    if is_jira_issue(project):
        jira_issue = project

    # print the status
    styled_log = get_styled_log(project, tags)
    if jira_issue is None:
        click.echo(f'{styled_log} {RED}unresolved{RESET}')
    else:
        click.echo(f'{styled_log} {GREEN}{jira_issue}{RESET}')

    # interact with user
    if is_interactive and jira_issue is None:
        jira_issue = ask()

    if not jira_issue:
        jira_issue = None
    return jira_issue


def get_styled_log(project, tags):
    out = MAGENTA + f'{project}'
    tag_delimeter = f'{RESET},{BLUE} '
    if len(tags):
        out += f'  {RESET}[{BLUE}{tag_delimeter.join(tags)}{RESET}]'
    return out


if __name__ == '__main__':
    pass

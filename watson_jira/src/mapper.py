import re
import yaml
import click
import os
from colorama import Fore, Style

mapping_rules = None


def is_jira_issue(string):
    """Returns True if input string is a valid JIRA issue key, else False"""
    jira_regex = r"^[A-Z]{1,10}-[0-9]+$"
    return bool(re.match(jira_regex, string))


def process_single_issue(category):
    return category["issue"]


def process_issue_per_project(category, project):
    if project in category["projects"].keys():
        return category["projects"][project]
    return None


def process_issue_specified_in_tag(tags):
    for tag in tags:
        if is_jira_issue(tag):
            return tag
    return None


def load_mapping_rules():
    stream = open(os.path.expanduser("~/.config/watson-jira/mapping-rules.yaml"))
    return yaml.safe_load(stream)


def ask():
    return click.prompt("Specify jira issue (leave empty to skip)", default="")


def map(project, tags, is_interactive):
    global mapping_rules

    if mapping_rules is None:
        mapping_rules = load_mapping_rules()

    # resolve jira issue
    jira_issue = None
    for category in mapping_rules["categories"]:
        if category["name"] in tags:
            if category["type"] == "single_issue":
                jira_issue = process_single_issue(category)
            elif category["type"] == "issue_per_project":
                jira_issue = process_issue_per_project(category, project)
            elif category["type"] == "issue_specified_in_tag":
                jira_issue = process_issue_specified_in_tag(tags)

    # print the status
    styled_log = get_styled_log(project, tags)
    if jira_issue is None:
        click.echo(f"{styled_log} {Fore.RED}unresolved{Fore.RESET}")
    else:
        click.echo(f"{styled_log} {Fore.GREEN}{jira_issue}{Fore.RESET}")

    # interact with user
    if is_interactive and jira_issue is None:
        jira_issue = ask()

    if not jira_issue:
        jira_issue = None
    return jira_issue


def get_styled_log(project, tags):
    out = Fore.MAGENTA + f"{project}"
    tag_delimeter = f"{Fore.RESET},{Fore.BLUE} "
    if len(tags):
        out += f"  {Fore.RESET}[{Fore.BLUE}{tag_delimeter.join(tags)}{Fore.RESET}]"
    return out


if __name__ == "__main__":
    pass

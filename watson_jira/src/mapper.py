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
    return yaml.load(stream)


def ask():
    return click.prompt("Specify jira issue (leave empty to skip)", default="")


def map(project, tags):
    global mapping_rules

    if mapping_rules is None:
        mapping_rules = load_mapping_rules()

    jira_issue = None
    for category in mapping_rules["categories"]:
        if category["name"] in tags:
            click.echo(Fore.YELLOW + f"{category['description']}" + Fore.RESET)
            if category["type"] == "single_issue":
                jira_issue = process_single_issue(category)
            elif category["type"] == "issue_per_project":
                jira_issue = process_issue_per_project(category, project)
            elif category["type"] == "issue_specified_in_tag":
                jira_issue = process_issue_specified_in_tag(tags)
            else:
                print("Invalid type of the significant tag")

    if jira_issue is None:
        click.echo(get_styled_log(project, tags) + " - unable to match mapping rule")
        jira_issue = ask()
    else:
        if not click.confirm(
            get_styled_log(project, tags) + f" will be logged to {jira_issue}",
            default=True,
        ):
            jira_issue = ask()

    if not jira_issue:
        jira_issue = None

    print("-" * 20)
    return jira_issue


def get_styled_log(project, tags):
    return Fore.MAGENTA + f"{project}" + Fore.BLUE + f" {tags}" + Fore.RESET


if __name__ == "__main__":
    pass

import yaml
import os
from jira import JIRA

config = None


def get():
    global config
    if config is None:
        path = os.path.expanduser("~/.config/watson-jira/config.yaml")
        print(f"Loading config from {path}")
        stream = open(path)
        config = yaml.safe_load(stream)

    return config


def prepare_jira_connection():
    config = get()
    if "jira" not in config:
        print("Config file must have Jira section set")
        return None
    jiraconfig = config["jira"]

    # Server must be specified
    if "server" not in jiraconfig:
        print("JIRA server must be set")
        return None

    # Prefer auth with personal access token
    if "username" in jiraconfig or "personalAccessToken" in jiraconfig:
        if "username" not in jiraconfig or "personalAccessToken" not in jiraconfig:
            print(
                "Auth with credentials requires both username and personalAccessToken to be set"
            )
            return None
        print(f"{jiraconfig['username']}")
        print(f"{jiraconfig['personalAccessToken']}")
        return JIRA(
            server=jiraconfig["server"],
            basic_auth=(jiraconfig["username"], jiraconfig["personalAccessToken"]),
        )

    # As second try to resolve and use cookie
    if "cookie" not in jiraconfig:
        print("Auth requires credentials or cookie to be set")
        return None

    headers = JIRA.DEFAULT_OPTIONS["headers"].copy()
    headers["cookie"] = f"{jiraconfig['cookie']}"
    return JIRA(server=jiraconfig["server"], options={"headers": headers})


if __name__ == "__main__":
    pass

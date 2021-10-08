import yaml
import os


class ConfigException(Exception):
    pass


config = None


def get():
    global config
    if config is None:
        path = os.path.expanduser("~/.config/watson-jira/config.yaml")
        print(f"Loading config from {path}")
        stream = open(path)
        config = yaml.safe_load(stream)

    return config


def jira():
    config = get()
    if config is None or "jira" not in config:
        raise ConfigException("Config file must have Jira section set")

    jiraconfig = config["jira"]
    jira = {
        "server": None,
        "auth": None,
        "cookie": None,
    }

    # Server must be specified
    if "server" not in jiraconfig:
        raise ConfigException("JIRA server must be set")

    jira["server"] = jiraconfig["server"]

    # Prefer auth with personal access token
    if "username" in jiraconfig or "personalAccessToken" in jiraconfig:
        if "username" not in jiraconfig or "personalAccessToken" not in jiraconfig:
            raise ConfigException(
                "Auth with credentials requires both username and personalAccessToken to be set"
            )

        jira["auth"] = (jiraconfig["username"], jiraconfig["personalAccessToken"])
        return jira

    # As second try to resolve and use cookie
    if "cookie" not in jiraconfig:
        raise ConfigException("Auth requires credentials or cookie to be set")

    jira["cookie"] = jiraconfig["cookie"]
    return jira


if __name__ == "__main__":
    pass

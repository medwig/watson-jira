import yaml
import os
from xdg import BaseDirectory


class ConfigException(Exception):
    pass


config = None


def set(data):
    global config
    try:
        # TODO: fix app name
        config_dir_path = BaseDirectory.save_config_path("watson-jir")
        path = os.path.join(config_dir_path, "config.yaml")
        stream = open(path, "w")
        yaml.safe_dump(data, stream)
        config = None
    except Exception:
        raise ConfigException("Failed to write config file")


def get():
    global config
    if config is None:
        try:
            # TODO: fix app name
            config_dir_path = BaseDirectory.load_first_config("watson-jir")
            if config_dir_path == None:
                raise ConfigException("Failed to find config dir")
            path = os.path.join(config_dir_path, "config.yaml")
            stream = open(path)
        except Exception:
            raise ConfigException("Failed to open config file")

        try:
            config = yaml.safe_load(stream)
        except Exception:
            raise ConfigException("Failed to parse config file")

    return config


def mappings():
    config = get()
    if config is None or "mappings" not in config:
        raise ConfigException("Config file must have `mappings` section")
    return config["mappings"]


def jira():
    config = get()
    if config is None or "jira" not in config:
        raise ConfigException("Config file must have `jira` section")

    jiraconfig = config["jira"]
    jira = {
        "server": None,
        "email": None,
        "apiToken": None,
        "pat": None,
        "cookie": None,
    }

    # Server must be specified
    if "server" not in jiraconfig:
        raise ConfigException("JIRA server must be set")

    jira["server"] = jiraconfig["server"]

    # Try to resolve personal access token
    if "personalAccessToken" in jiraconfig:
        jira["pat"] = jiraconfig["personalAccessToken"]
        return jira

    # Try to resolve email and API token
    if "email" in jiraconfig or "apiToken" in jiraconfig:
        if "email" not in jiraconfig or "apiToken" not in jiraconfig:
            raise ConfigException(
                "Auth method with email and API token requires both to be set"
            )

        jira["email"] = jiraconfig["email"]
        jira["apiToken"] = jiraconfig["apiToken"]
        return jira

    # Try to resolve cookie
    if "cookie" in jiraconfig:
        jira["cookie"] = jiraconfig["cookie"]
        return jira

    raise ConfigException("No authentication method configured")


if __name__ == "__main__":
    pass

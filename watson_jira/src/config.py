"""Loads and parses the config file for watson-jira"""

import os
import yaml

from xdg import BaseDirectory


class ConfigException(Exception):
    pass


def set_config(data):
    try:
        config_dir_path = BaseDirectory.save_config_path('watson-jira')
        path = os.path.join(config_dir_path, 'config.yaml')
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f)
    except Exception as exc:
        raise ConfigException('Failed to write config file') from exc


def load_config():
    try:
        config_dir_path = BaseDirectory.load_first_config('watson-jira')
        assert config_dir_path is not None, 'Failed to find config dir'
        path = os.path.join(config_dir_path, 'config.yaml')
        with open(path, encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as exc:
        raise ConfigException('Failed to parse config file') from exc

    return config


def get_mappings():
    config = load_config()
    if config is None or 'mappings' not in config:
        raise ConfigException('Config file must have `mappings` section')
    return config['mappings']


def get_jira_config():
    config = load_config()
    if config is None or 'jira' not in config:
        raise ConfigException('Config file must have `jira` section')

    jiraconfig = config['jira']
    jira = {
        'server': None,
        'email': None,
        'apiToken': None,
        'pat': None,
        'cookie': None,
    }

    # Server must be specified
    if 'server' not in jiraconfig:
        raise ConfigException('JIRA server must be set')

    jira['server'] = jiraconfig['server']

    # Try to resolve personal access token
    if 'personalAccessToken' in jiraconfig:
        jira['pat'] = jiraconfig['personalAccessToken']
        return jira

    # Try to resolve email and API token
    if 'email' in jiraconfig or 'apiToken' in jiraconfig:
        if 'email' not in jiraconfig or 'apiToken' not in jiraconfig:
            raise ConfigException(
                'Auth method with email and API token requires both to be set'
            )

        jira['email'] = jiraconfig['email']
        jira['apiToken'] = jiraconfig['apiToken']
        return jira

    # Try to resolve cookie
    if 'cookie' in jiraconfig:
        jira['cookie'] = jiraconfig['cookie']
        return jira

    raise ConfigException('No authentication method configured')


if __name__ == '__main__':
    pass

"""Loads and parses the config file for watson-jira"""

import os
import yaml

from xdg import BaseDirectory


class ConfigException(Exception):
    pass


def get_config_path():
    config_dir_path = BaseDirectory.load_first_config('watson-jira')
    assert config_dir_path is not None, 'Failed to find config dir'
    return os.path.join(config_dir_path, 'config.yaml')


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
        config_path = get_config_path()
        with open(config_path, encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise
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

    jira_config = config['jira']
    jira = {
        'server': None,
        'email': None,
        'apiToken': None,
        'pat': None,
        'cookie': None,
    }

    # Server must be specified
    try:
        jira['server'] = jira_config['server']
    except KeyError as exc:
        raise ConfigException('JIRA server must be set') from exc

    # Try to resolve personal access token
    if 'personalAccessToken' in jira_config:
        jira['pat'] = jira_config['personalAccessToken']
        return jira

    # Try to resolve email and API token
    if 'email' in jira_config or 'apiToken' in jira_config:
        try:
            jira['email'] = jira_config['email']
            jira['apiToken'] = jira_config['apiToken']
            return jira
        except KeyError as exc:
            raise ConfigException('Auth via email and API token requires both to be set') from exc

    # Try to resolve cookie
    if 'cookie' in jira_config:
        jira['cookie'] = jira_config['cookie']
        return jira

    raise ConfigException('No authentication method configured')


if __name__ == '__main__':
    pass

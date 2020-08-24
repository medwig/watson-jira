import yaml
import os

config = None

def get():
    global config
    if config is None:
        path = os.path.expanduser("~/.config/watson-jira/config.yaml")
        print(f"Loading config from {path}")
        stream = open(path)
        config = yaml.safe_load(stream)

    return config

if __name__ == "__main__":
    pass
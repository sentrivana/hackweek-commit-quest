import sys

import yaml


with open("../secrets.yaml") as stream:
    try:
        SECRETS = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Failed to load secrets")
        sys.exit(1)

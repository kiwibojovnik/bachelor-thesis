import json


def load_credentials(credentials_type):
    with open(f'config/config.json') as f:
        config_data = json.load(f)

    return config_data[credentials_type]

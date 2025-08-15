import os

from dotenv import load_dotenv

from dev_observer.env_detection import detect_server_env
from dev_observer.server.env import ServerEnv
from dev_observer.settings import Settings

secrets_file = os.environ.get("DEV_OBSERVER_SECRETS_FILE", None)
if secrets_file is not None and len(secrets_file.strip()) > 0 and os.path.exists(secrets_file) and os.path.isfile(
        secrets_file):
    load_dotenv(secrets_file)

env_file = os.environ.get("DEV_OBSERVER_ENV_FILE", None)
if env_file is not None and len(env_file.strip()) > 0 and os.path.exists(env_file) and os.path.isfile(env_file):
    load_dotenv(env_file)

Settings.model_config["toml_file"] = os.environ.get("DEV_OBSERVER_CONFIG_FILE", None)
env: ServerEnv = detect_server_env(Settings())

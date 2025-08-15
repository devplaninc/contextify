import logging
import os

from dotenv import load_dotenv

import dev_observer.log
from dev_observer.env_detection import detect_server_env
from dev_observer.server.env import ServerEnv
from dev_observer.settings import Settings

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)

# Or suppress all AWS-related debug messages
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('aiobotocore').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)


secrets_file = os.environ.get("DEV_OBSERVER_SECRETS_FILE", None)
if secrets_file is not None and len(secrets_file.strip()) > 0 and os.path.exists(secrets_file) and os.path.isfile(
        secrets_file):
    load_dotenv(secrets_file)

env_file = os.environ.get("DEV_OBSERVER_ENV_FILE", None)
if env_file is not None and len(env_file.strip()) > 0 and os.path.exists(env_file) and os.path.isfile(env_file):
    load_dotenv(env_file)

Settings.model_config["toml_file"] = os.environ.get("DEV_OBSERVER_CONFIG_FILE", None)
env: ServerEnv = detect_server_env(Settings())

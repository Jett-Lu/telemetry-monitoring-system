import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
ENV_FILE_PATH = os.path.join(PROJECT_ROOT, ".env")
REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "CRUX_API_KEY",
    "UPTIMEROBOT_API_KEY",
]
DEFAULT_TRACKED_ORIGIN = "https://www.mcmaster.ca/"


def load_env_file(env_file_path=ENV_FILE_PATH, override=True):
    if not os.path.exists(env_file_path):
        return

    with open(env_file_path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and (override or key not in os.environ):
                os.environ[key] = value


def validate_required_env_vars(required_vars=None):
    required_vars = required_vars or REQUIRED_ENV_VARS
    missing_vars = [name for name in required_vars if not os.getenv(name)]

    if missing_vars:
        missing_list = ", ".join(missing_vars)
        raise RuntimeError(
            f"Missing required environment variables: {missing_list}. "
            f"Add them to {ENV_FILE_PATH} or your environment before starting SentinelLog."
        )


def load_and_validate_environment():
    load_env_file()
    validate_required_env_vars()


def get_tracked_origin():
    return os.getenv("TRACKED_ORIGIN", DEFAULT_TRACKED_ORIGIN)

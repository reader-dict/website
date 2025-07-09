# WSGI configuration for production deployment on EX2.
import logging

import sentry_sdk

from src import __version__, constants, server

logging.basicConfig(
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=constants.LOGS,
    level=logging.INFO,
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
sentry_sdk.init(constants.SENTRY_DSN_BACKEND, environment=constants.SENTRY_ENV_PROD, release=__version__)

application = server.app

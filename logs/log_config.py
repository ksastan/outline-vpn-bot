import sys
import logging


def log_setup(log_level: str):
    logs = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logs.addHandler(handler)
    # set logging level
    if log_level.upper() == "ERROR":
        logs.setLevel(logging.ERROR)
    elif log_level.upper() == "INFO":
        logs.setLevel(logging.INFO)
    elif log_level.upper() == "DEBUG":
        logs.setLevel(logging.DEBUG)
    elif log_level.upper() == "CRITICAL":
        logs.setLevel(logging.CRITICAL)
    else:
        logs.setLevel(logging.ERROR)


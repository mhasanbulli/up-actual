import os


def get_token():
    up_token = os.getenv("UP_TOKEN")

    if up_token is None:
        raise OSError("UP_TOKEN environment variable is not set.")
    return up_token
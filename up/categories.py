import ujson

from up.classes import UpAPI

up_api = UpAPI()


def get_categories() -> list:
    response = up_api.get_endpoint_response(up_api.categories_url)
    response_json = ujson.loads(response.text)

    all_categories = [category["id"] for category in response_json["data"]]

    return all_categories


get_categories()

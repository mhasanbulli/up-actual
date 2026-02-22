import datetime

import pytest
from up.classes import Categories, QueryParams, SimplifiedCategories, UpAPI


@pytest.fixture
def up_api(monkeypatch: pytest.MonkeyPatch) -> UpAPI:
    monkeypatch.setenv("UP_TOKEN", "test-token")
    return UpAPI()


def test_up_api_url(up_api: UpAPI):
    assert up_api.up_api_url == "https://api.up.com.au/api/v1"


def test_up_api_headers(up_api: UpAPI):
    assert up_api.headers == {"Authorization": "Bearer test-token"}


def test_up_api_accounts_url(up_api: UpAPI):
    assert up_api.accounts_url == "https://api.up.com.au/api/v1/accounts"


def test_up_api_ping_url(up_api: UpAPI):
    assert up_api.ping_url == "https://api.up.com.au/api/v1/util/ping"


def test_up_api_transactions_url(up_api: UpAPI):
    assert up_api.transactions_url == "https://api.up.com.au/api/v1/transactions"


def test_up_api_categories_url(up_api: UpAPI):
    assert up_api.categories_url == "https://api.up.com.au/api/v1/categories"


def test_query_params_get_params():
    params = QueryParams(
        start_date=datetime.datetime(2025, 7, 10, 12, 0, 0, tzinfo=datetime.timezone.utc),
        page_size=50,
        days_offset=5,
    )
    result = params.get_params()

    assert result["page[size]"] == 50
    assert "filter[since]" in result


def test_simplified_category_label_known_category():
    assert SimplifiedCategories.get_simplified_category_label(Categories.GROCERIES) == "Groceries"


def test_simplified_category_label_returns_none_for_none():
    assert SimplifiedCategories.get_simplified_category_label(None) is None


@pytest.mark.parametrize(
    ("category", "expected_label"),
    [
        (Categories.ADULT, "General"),
        (Categories.EVENTS_GIGS, "Entertainment"),
        (Categories.HAIR_BEAUTY, "Personal Care"),
        (Categories.INTERNET, "Bills & Utilities"),
        (Categories.RENT_MORTGAGE, "Rent & Mortgage"),
        (Categories.TV_MUSIC_STREAMING, "Subscriptions"),
        (Categories.PUBLIC_TRANSPORT, "Transport"),
        (Categories.CLOTHING_ACCESSORIES, "Clothing & Accessories"),
        (Categories.RESTAURANTS_CAFES, "Eating Out"),
        (Categories.INVESTMENTS, "Income"),
        (Categories.TECHNOLOGY, "Technology"),
    ],
)
def test_simplified_category_label_all_groups(category: Categories, expected_label: str):
    assert SimplifiedCategories.get_simplified_category_label(category) == expected_label

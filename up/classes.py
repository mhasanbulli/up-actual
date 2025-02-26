import datetime
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Annotated

import requests
from actual import Actual
from requests import Response

from up.utils import get_rfc_3339_date_offset, get_token, get_url


@dataclass
class UpAPI:
    @property
    def up_api_url(self) -> str:
        return "https://api.up.com.au/api/v1"

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {get_token()}"}

    @property
    def accounts_url(self) -> str:
        return f"{self.up_api_url}/accounts"

    @property
    def ping_url(self) -> str:
        return f"{self.up_api_url}/util/ping"

    @property
    def transactions_url(self) -> str:
        return f"{self.up_api_url}/transactions"

    @property
    def categories_url(self) -> str:
        return f"{self.up_api_url}/categories"

    def get_endpoint_response(self, url: str, url_params: dict | None = None) -> Response:
        url = get_url(url, url_params)
        # TODO: Update timeout once the endpoint issues ate resolved
        response = requests.get(url=url, headers=self.headers, timeout=30)

        return response


@dataclass
class UpAccount:
    name: str
    url: str
    next_url: str | None = None


@dataclass
class AccountBatchTransactions:
    account_name: str
    transactions: list
    next_url: str | None = None


@dataclass
class QueryParams:
    start_date: Annotated[datetime.datetime, field(default_factory=datetime.datetime.now)]
    page_size: int = 100
    days_offset: int = 1

    def get_params(self) -> dict:
        return {
            "page[size]": self.page_size,
            "filter[since]": get_rfc_3339_date_offset(start_date=self.start_date, days_offset=self.days_offset),
        }


@dataclass
class ActualSession:
    url: str
    password: str
    file: str
    encryption_password: str

    def get_actual_session(self) -> Actual:
        return Actual(
            base_url=self.url, password=self.password, file=self.file, encryption_password=self.encryption_password
        )


class Categories(StrEnum):
    ADULT = "adult"
    APPS_GAMES_SOFTWARE = "games-and-software"
    BOOZE = "booze"
    CAR = "car-insurance-and-maintenance"
    CHILDREN_FAMILY = "family"
    CLOTHING_ACCESSORIES = "clothing-and-accessories"
    CYCLING = "cycling"
    EDUCATION_STUDENT_LOANS = "education-and-student-loans"
    EVENTS_GIGS = "events-and-gigs"
    FITNESS_WELLBEING = "fitness-and-wellbeing"
    FUEL = "fuel"
    GIFTS_CHARITY = "gifts-and-charity"
    GOOD_LIFE = "good-life"
    GROCERIES = "groceries"
    HAIR_BEAUTY = "hair-and-beauty"
    HEALTH_MEDICAL = "health-and-medical"
    HOBBIES = "hobbies"
    HOLIDAYS_TRAVEL = "holidays-and-travel"
    HOME = "home"
    HOMEWARE_APPLIANCES = "homeware-and-appliances"
    INTERNET = "internet"
    INVESTMENTS = "investments"
    LIFE_ADMIN = "life-admin"
    LOTTERY_GAMBLING = "lottery-and-gambling"
    MAINTENANCE_IMPROVEMENTS = "home-maintenance-and-improvements"
    MOBILE_PHONE = "mobile-phone"
    NEWS_MAGAZINES_BOOKS = "news-magazines-and-books"
    PARKING = "parking"
    PERSONAL = "personal"
    PETS = "pets"
    PUBS_BARS = "pubs-and-bars"
    PUBLIC_TRANSPORT = "public-transport"
    RATES_INSURANCE = "home-insurance-and-rates"
    RENT_MORTGAGE = "rent-and-mortgage"
    REPAYMENTS = "car-repayments"
    RESTAURANTS_CAFES = "restaurants-and-cafes"
    TAKEAWAY = "takeaway"
    TAXIS_SHARE_CARS = "taxis-and-share-cars"
    TECHNOLOGY = "technology"
    TOBACCO_VAPING = "tobacco-and-vaping"
    TOLLS = "toll-roads"
    TRANSPORT = "transport"
    TV_MUSIC_STREAMING = "tv-and-music"
    UTILITIES = "utilities"


class SimplifiedCategories(Enum):
    GENERAL = (
        "General",
        {
            Categories.ADULT,
            Categories.CAR,
            Categories.CYCLING,
            Categories.FUEL,
            Categories.CHILDREN_FAMILY,
            Categories.EDUCATION_STUDENT_LOANS,
            Categories.GOOD_LIFE,
            Categories.PETS,
            Categories.LIFE_ADMIN,
            Categories.TOBACCO_VAPING,
            Categories.TECHNOLOGY,
            Categories.GIFTS_CHARITY,
            Categories.HOME,
            Categories.HOMEWARE_APPLIANCES,
            Categories.MAINTENANCE_IMPROVEMENTS,
        },
    )
    ENTERTAINMENT = (
        "Entertainment",
        {
            Categories.APPS_GAMES_SOFTWARE,
            Categories.EVENTS_GIGS,
            Categories.BOOZE,
            Categories.HOBBIES,
            Categories.HOLIDAYS_TRAVEL,
            Categories.LOTTERY_GAMBLING,
            Categories.NEWS_MAGAZINES_BOOKS,
        },
    )
    PERSONAL_CARE = (
        "Personal Care",
        {
            Categories.HAIR_BEAUTY,
            Categories.FITNESS_WELLBEING,
            Categories.HEALTH_MEDICAL,
            Categories.PERSONAL,
        },
    )
    GROCERIES = (
        "Groceries",
        {
            Categories.GROCERIES,
        },
    )
    BILLS_UTILITIES = (
        "Bills & Utilities",
        {
            Categories.INTERNET,
            Categories.UTILITIES,
            Categories.RATES_INSURANCE,
        },
    )
    RENT_MORTGAGE = (
        "Rent & Mortgage",
        {
            Categories.RENT_MORTGAGE,
        },
    )
    SUBSCRIPTIONS = (
        "Subscriptions",
        {
            Categories.TV_MUSIC_STREAMING,
            Categories.MOBILE_PHONE,
        },
    )
    TRANSPORT = (
        "Transport",
        {
            Categories.PUBLIC_TRANSPORT,
            Categories.TAXIS_SHARE_CARS,
            Categories.PARKING,
            Categories.TOLLS,
            Categories.TRANSPORT,
        },
    )
    CLOTHING_ACCESSORIES = (
        "Clothing & Accessories",
        {
            Categories.CLOTHING_ACCESSORIES,
        },
    )
    EATING_OUT = (
        "Eating Out",
        {
            Categories.RESTAURANTS_CAFES,
            Categories.TAKEAWAY,
            Categories.PUBS_BARS,
        },
    )
    INCOME = (
        "Income",
        {
            Categories.INVESTMENTS,
            Categories.REPAYMENTS,
        },
    )

    @classmethod
    def get_simplified_category_label(cls, category_class: Categories | None) -> str | None:
        try:
            for category in cls:
                if category_class in category.value[1]:
                    return category.value[0]
        except ValueError:
            return None

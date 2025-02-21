from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ACTUAL__",
    )

    url: SecretStr
    password: SecretStr
    encryption_password: SecretStr
    file: str

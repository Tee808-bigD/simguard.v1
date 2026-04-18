"""Config — all secrets from env vars only."""
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    app_env: str = "production"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    database_url: str = "sqlite+aiosqlite:///./simguard.db"
    nac_api_key: str = ""
    nac_api_host: str = "network-as-code.p-eu.rapidapi.com"
    anthropic_api_key: str = ""
    rate_limit_per_minute: int = 30
    rate_limit_burst: int = 10
    auth_max_attempts: int = 5
    auth_lockout_minutes: int = 15
    max_transaction_amount: float = 1_000_000
    max_phone_length: int = 20
    max_name_length: int = 100
    max_payload_bytes: int = 10240
    nac_auth_url: str = "https://nac-authorization-server.p-eu.rapidapi.com"
    nac_auth_host: str = "nac-authorization-server.nokia.rapidapi.com"
    nac_metadata_url: str = "https://well-known-metadata.p-eu.rapidapi.com"
    nac_metadata_host: str = "well-known-metadata.nokia.rapidapi.com"
    nac_nv_url: str = "https://number-verification.p-eu.rapidapi.com"
    nac_nv_host: str = "number-verification.nokia.rapidapi.com"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

from typing import Literal

from pydantic import BaseSettings


class Config(BaseSettings):
    ebay_api_key: str
    """eBay API key for their REST API"""
    ebay_api_url: str
    """Base URL for eBay search API"""
    db_path: str = "data/db.sqlite"
    """Path to the SQLite database"""
    request_timeout: int = 10
    """Timeout for any external requests (in seconds)"""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    class Config:
        env_prefix = "app_"

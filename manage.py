import asyncio
import os
from typing import Optional

import typer
import uvicorn

from ebay_alerts_service.config import Config
from ebay_alerts_service.db import DbConnection

cli = typer.Typer(name="CLI for Metrics Search API")


@cli.command("init_db")
def init_db():
    """Create SQLite database with schema"""
    config = Config()
    if os.path.exists(config.db_path):
        print("DB already exists and will be deleted during the loading of dataset.")
        decision = input("Would you like to continue (y/n)? ")
        if decision != "y":
            return
        os.remove(config.db_path)

    loop = asyncio.get_event_loop()
    conn = DbConnection(config.db_path, echo=True)
    loop.run_until_complete(conn.init_schema())


@cli.command("run")
def run(
    host: Optional[str] = typer.Option("0.0.0.0", envvar="APP_HOST"),
    port: int = typer.Option(8000, envvar="APP_PORT"),
):
    """Run application"""
    uvicorn.run("ebay_alerts_service.app:api", host=host, port=port)


if __name__ == "__main__":
    cli()

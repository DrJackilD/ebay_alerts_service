import logging
from typing import Type

from fastapi import FastAPI
from sqlalchemy import select

from ebay_alerts_service import db
from ebay_alerts_service.config import Config
from ebay_alerts_service.processors import get_processors
from ebay_alerts_service.routers import alerts
from ebay_alerts_service.scheduler import AlertsScheduler
from ebay_alerts_service.utils import setup_logging

logger = logging.getLogger(__name__)

api = FastAPI()
api.include_router(alerts.router)


async def on_create_object(model: Type[db.Base], obj_id: int):
    logger.debug(f"Model created: {model}, id: {obj_id}")
    if model == db.Alert:
        alert = (
            await api.state.conn.select(select(model).where(model.id == obj_id))
        ).scalar()
        api.state.scheduler.upsert_job(alert)


async def on_update_object(model: Type[db.Base], obj_id: int):
    logger.debug(f"Model updated: {model}, id: {obj_id}")
    if model == db.Alert:
        alert = (
            await api.state.conn.select(select(model).where(model.id == obj_id))
        ).scalar()
        api.state.scheduler.upsert_job(alert)


async def on_delete_object(model: Type[db.Base], obj_id: int):
    logger.debug(f"Model deleted: {model}, id: {obj_id}")
    if model == db.Alert:
        api.state.scheduler.delete_job(obj_id)


@api.on_event("startup")
async def init_application():
    config = Config()
    setup_logging(config)
    conn = db.DbConnection(
        config.db_path,
        on_create=on_create_object,
        on_update=on_update_object,
        on_delete=on_delete_object,
    )
    api.state.config = config
    api.state.conn = conn
    current_alerts = (await conn.select(select(db.Alert))).scalars()
    scheduler = AlertsScheduler(config, get_processors(), list(current_alerts))
    api.state.scheduler = scheduler
    scheduler.start()


@api.on_event("shutdown")
async def shutdown_application():
    await api.state.conn.close()
    api.state.scheduler.shutdown()

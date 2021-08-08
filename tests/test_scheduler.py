import asyncio

import pytest
from aiocron import Cron

from ebay_alerts_service import db
from ebay_alerts_service.config import Config
from ebay_alerts_service.scheduler import AlertsScheduler


async def process_job(alert: db.Alert, output_queue: asyncio.Queue, lock: asyncio.Lock):
    if lock.locked():
        return

    async with lock:
        await output_queue.put(alert)


@pytest.mark.asyncio
async def test_schedule_cron_job(db_connection: db.DbConnection):
    output_queue = asyncio.Queue()
    config = Config()
    alerts = [db.Alert(email="someone@test.local", phrase="test phrase", interval=1)]
    await db_connection.bulk_create(alerts)
    scheduler = AlertsScheduler(config, [], alerts)
    # Here we mock our cron job to run each second instead of every minute
    # and run our mock function
    scheduler.jobs[alerts[0].id] = Cron(
        "* * * * * */1",
        func=process_job,
        args=(alerts[0], output_queue, asyncio.Lock()),
    )
    scheduler.start()
    res = await output_queue.get()
    assert res == alerts[0]

import asyncio
import logging
import typing as t

from pydantic import BaseModel, EmailStr

if t.TYPE_CHECKING:
    from ebay_alerts_service.config import Config
    from ebay_alerts_service.scheduler import JobParams

logger = logging.getLogger(__name__)


class AlertJobResult(BaseModel):
    """
    Class to keep results
    """

    email: EmailStr
    results: t.List[dict]


async def alert_job(
    job_params: "JobParams",
    on_result: t.Callable[[AlertJobResult], t.Awaitable[None]],
    on_error: t.Callable[["JobParams", Exception], t.Awaitable[None]],
    sync_lock: asyncio.Lock,
    config: "Config",
):
    """
    Checks the eBay API, get the results list and send it to the result callback
    :param job_params: contains JobParams instance with details about this job
    :param on_result: callback function to call with results
    :param on_error: callback function to call with any errors
    :param sync_lock: lock to keep one instance of each cron job at a time
    :param config: instance of application settings
    """
    if sync_lock.locked():
        logger.debug(f"Cron job locked for {job_params}. Skipping.")
        return

    async with sync_lock:
        try:
            result = AlertJobResult(email=job_params.email, results=[])
            await on_result(result)
            logger.info(f"Job finished: {job_params}")
        except Exception as e:
            await on_error(job_params, e)
            logger.error(f"Job failed; params: {job_params}")

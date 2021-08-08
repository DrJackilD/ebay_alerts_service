import asyncio
import logging
import typing as t

from aiocron import Cron
from pydantic import BaseModel, EmailStr

from ebay_alerts_service import db
from ebay_alerts_service.config import Config
from ebay_alerts_service.job import alert_job
from ebay_alerts_service.processors.base import AbstractProcessor

if t.TYPE_CHECKING:
    from ebay_alerts_service.job import AlertJobResult

logger = logging.getLogger(__name__)


class JobParams(BaseModel):
    """
    Simple model to keep alert data job details
    """

    id: int
    email: EmailStr
    phrase: str

    class Config:
        orm_mode = True


class AlertsScheduler:
    """
    This is a scheduler class for all alerts created in the system
    """

    def __init__(
        self,
        config: Config,
        processors: t.List[AbstractProcessor],
        alerts: t.List[db.Alert],
    ):
        self.config = config
        self.processors = processors
        self.jobs: t.Dict[int, Cron] = self._create_jobs(alerts)

    def start(self):
        """
        Starts all scheduled jobs
        """

        for j in self.jobs.values():
            j.start()
            logger.debug(f"Job started: {j}")
        logger.info("Jobs are scheduled")

    def shutdown(self):
        """
        Stops all cron jobs and processors and do any other required tasks for shutdown
        """
        for job in self.jobs.values():
            job.stop()
            logger.debug(f"Job stopped: {job}")
        logger.info("Shutdown completed")

    async def publish(self, result: "AlertJobResult"):
        """
        Method used by alert's jobs to publish their results
        """
        loads = [loader.load(result) for loader in self.processors]
        await asyncio.gather(*loads)

    async def on_error_callback(self, job_params: JobParams, exc: Exception):
        """
        Method to post any exceptions during alert processing
        """
        logger.error(
            f"Exception during job for alert with id {job_params.id}", exc_info=exc
        )

    def upsert_job(self, alert: db.Alert):
        """Insert or update cron job for given alert"""
        exist = self.jobs.pop(alert.id, None)
        if exist:
            exist.stop()
            logger.debug(f"Cron job stopped for alert {alert.id}")
        cron = self._create_cron_from_alert(alert)
        self.jobs[alert.id] = cron
        cron.start()
        if exist:
            logger.debug(f"Cron job updated for alert {alert.id}")
        else:
            logger.debug(f"Cron job created for alert {alert.id}")

    def delete_job(self, alert_id: int):
        """Stops the cron job and remove it from the jobs"""
        cron = self.jobs.pop(alert_id, None)
        if cron:
            cron.stop()
            logger.debug(f"Cron job deleted for alert {alert_id}")

    def _create_cron_from_alert(self, alert: db.Alert) -> Cron:
        schedule = f"*/{alert.interval} * * * *"
        job_params = JobParams.from_orm(alert)
        cron = Cron(
            schedule,
            func=alert_job,
            args=(
                job_params,
                self.publish,
                self.on_error_callback,
                asyncio.Lock(),
                self.config,
            ),
        )
        return cron

    def _create_jobs(self, alerts: t.List[db.Alert]) -> t.Dict[int, Cron]:
        """
        Create cron job for each alert in the list of alerts
        :return: dict with prepared Cron jobs for each entry
        """
        jobs = {}
        logger.info(f"Create jobs for {len(alerts)} alerts")
        for alert in alerts:
            cron = self._create_cron_from_alert(alert)
            jobs[alert.id] = cron
        return jobs

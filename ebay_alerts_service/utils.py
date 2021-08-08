import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ebay_alerts_service.config import Config

logger = logging.getLogger(__name__)


def setup_logging(config: "Config"):
    logging.basicConfig(
        level=logging.getLevelName(config.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

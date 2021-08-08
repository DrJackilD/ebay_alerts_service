"""
This package contains processors.
Each processor get incoming results and do something with them,
e. g. EmailProcessor could take results and send email to somewhere.
"""
from typing import List

from ebay_alerts_service.processors.base import AbstractProcessor


def get_processors() -> List[AbstractProcessor]:
    """Get processors for the scheduler"""
    return []

from abc import ABC, abstractmethod
from typing import Any


class AbstractProcessor(ABC):
    """
    Interface for all classes which want to works as result processor
    """

    @abstractmethod
    async def load(self, result: Any):
        """
        Loads result
        :param result: result to process
        """
        pass

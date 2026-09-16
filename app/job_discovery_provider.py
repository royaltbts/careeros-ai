from abc import ABC, abstractmethod

from app.models.job_discovery import JobDiscovery


class JobDiscoveryProvider(ABC):
    @abstractmethod
    def discover(self) -> list[JobDiscovery]:
        raise NotImplementedError

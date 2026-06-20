from abc import ABC, abstractmethod


class IFileStorage(ABC):

    @abstractmethod
    async def save(self, filename: str, content: bytes) -> str:
        pass

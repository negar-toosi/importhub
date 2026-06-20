from abc import ABC, abstractmethod

class IImportDispatcher(ABC):

    @abstractmethod
    async def dispatch(
        self,
        import_id,
        file_path
    ):
        pass
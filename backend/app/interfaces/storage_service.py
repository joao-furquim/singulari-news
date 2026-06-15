from abc import ABC, abstractmethod


class IStorageService(ABC):
    @abstractmethod
    async def upload(self, key: str, file_bytes: bytes, content_type: str) -> str:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

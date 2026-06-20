import os
import uuid

from src.domain.interfaces.file_storage import IFileStorage


class LocalFileStorage(IFileStorage):
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        suffix = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4()}{suffix}"
        path = os.path.join(self.upload_dir, unique_name)
        with open(path, "wb") as f:
            f.write(content)
        return path

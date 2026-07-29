import os
from abc import ABC, abstractmethod

import aiofiles


class StorageProvider(ABC):
    @abstractmethod
    async def save_file(self, file_data: bytes, folder_path: str, filename: str) -> str:
        """Saves file contents and returns the relative or absolute storage path."""
        pass

    @abstractmethod
    async def read_file(self, file_path: str) -> bytes:
        """Reads file content from the given path."""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Deletes file at the target path."""
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        os.makedirs(root_dir, exist_ok=True)

    def _get_absolute_path(self, target_path: str) -> str:
        # Prevent Directory Traversal (Part 9 Security)
        abs_root = os.path.abspath(self.root_dir)
        abs_target = os.path.abspath(os.path.join(abs_root, target_path))
        if not abs_target.lower().startswith(abs_root.lower()):
            raise ValueError("Directory traversal attempt blocked")
        return abs_target

    async def save_file(self, file_data: bytes, folder_path: str, filename: str) -> str:
        dest_dir = self._get_absolute_path(folder_path)
        os.makedirs(dest_dir, exist_ok=True)

        relative_path = os.path.join(folder_path, filename)
        abs_path = self._get_absolute_path(relative_path)

        async with aiofiles.open(abs_path, "wb") as f:
            await f.write(file_data)

        return relative_path

    async def read_file(self, file_path: str) -> bytes:
        abs_path = self._get_absolute_path(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError("The target storage object does not exist")

        async with aiofiles.open(abs_path, "rb") as f:
            return await f.read()

    async def delete_file(self, file_path: str) -> bool:
        try:
            abs_path = self._get_absolute_path(file_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
                return True
            return False
        except Exception:
            return False

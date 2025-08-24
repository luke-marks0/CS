from __future__ import annotations

import copy
from dataclasses import dataclass
from functools import wraps

from framework.simulator import make_simulator


@dataclass
class File:
    name: str
    size: int
    timestamp: int = 0
    ttl: int | None = None


class FileStorage:
    def __init__(self):
        self.files = {}
        self.backups = {}

    def _is_alive(self, timestamp: int, file_name: str):
        if not file_name in self.files:
            raise RuntimeError("File with this name does not exist.")
        file = self.files[file_name]
        if file.ttl is None:
            return True
        return (file.timestamp + file.ttl) > timestamp
    
    def _backup(self, timestamp: int):
        self.backups[timestamp] = copy.deepcopy(self.files)

    def file_upload(self, file_name: str, size: int):
        if file_name in self.files:
            raise RuntimeError("File with this name already exists.")
        self.files[file_name] = File(name=file_name, size=size)

    def file_upload_at(self, timestamp: int, file_name: str, size: int, ttl: int = None):
        if file_name in self.files:
            raise RuntimeError("File with this name already exists.")
        self.files[file_name] = File(name=file_name, size=size, timestamp=timestamp, ttl=ttl)
        self._backup(timestamp)

    def file_get(self, file_name: str):
        if file_name in self.files:
            return self.files[file_name].size
        return None

    def file_get_at(self, timestamp: int, file_name: str):
        if file_name in self.files and self._is_alive(timestamp, file_name):
            return self.files[file_name].size
        return None

    def file_copy(self, source: str, dest: str):
        if not source in self.files:
            raise RuntimeError("Source file does not exist.")
        self.files[dest] = copy.deepcopy(self.files[source])
        self.files[dest].name = dest

    def file_copy_at(self, timestamp: int, source: str, dest: str):
        if source in self.files and self._is_alive(timestamp, source):
            self.files[dest] = copy.deepcopy(self.files[source])
            self.files[dest].name = dest
            self.files[dest].timestamp = timestamp
            self._backup(timestamp)
        else:
            raise RuntimeError("Source file does not exist.")

    def file_search(self, prefix: str):
        sorted_files = sorted(self.files.items(), key= lambda f: (-f[1].size, f[1].name))
        top_10 = []
        for file in sorted_files:
            if len(top_10) >= 10:
                break
            elif file[1].name.startswith(prefix):
                top_10.append(file[1].name)
        return top_10

    def file_search_at(self, timestamp: int, prefix: str):
        sorted_files = sorted(self.files.items(), key= lambda f: (-f[1].size, f[1].name))
        top_10 = []
        for file in sorted_files:
            if len(top_10) >= 10:
                break
            elif file[1].name.startswith(prefix) and self._is_alive(timestamp, file[1].name):
                top_10.append(file[1].name)
        return top_10

    def rollback(self, timestamp: int):
        sorted_backups = sorted(self.backups.items())
        backed_up = 0
        for backup in sorted_backups:
            if timestamp >= backup[0]:
                self.files = copy.deepcopy(self.backups[backup[0]])
                for file in self.files.values():
                    file.timestamp = timestamp
                backed_up = 1
        if not backed_up:
            self.files = {}

simulate_coding_framework = make_simulator(FileStorage)
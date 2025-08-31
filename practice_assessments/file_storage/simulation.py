from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy

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

    def _is_alive(self, timestamp: int, name: str):
        if not name in self.files:
            raise RuntimeError("File does not exist.")
        file = self.files[name]
        if file.ttl == None:
            return True
        return timestamp < file.timestamp + file.ttl

    def _backup(self, timestamp: int) -> None:
        self.backups[timestamp] = deepcopy(self.files)

    def file_upload(self, name: str, size: int) -> None:
        if not name in self.files:
            self.files[name] = File(name=name, size=size)
        else:
            raise RuntimeError("File already exists.")
    
    def file_get(self, name: str) -> int:
        if name in self.files:
            return self.files[name].size
        return None
    
    def file_copy(self, source: str, dest: str) -> None:
        if source in self.files:
            self.files[dest] = deepcopy(self.files[source])
            self.files[dest].name = dest
        else:
            raise RuntimeError("Source file does not exist.")

    def file_search(self, prefix: str):
        sorted_files = sorted(self.files.items(), key=lambda f:(-f[1].size, f[1].name))
        top_10 = []
        for file in sorted_files:
            if len(top_10) >= 10:
                break
            if file[1].name.startswith(prefix):
                top_10.append(file[1].name)
        return top_10

    def file_upload_at(self, timestamp: int, name: str, size: int, ttl: int = None) -> None:
        if not name in self.files:
            self.files[name] = File(name=name, size=size, timestamp=timestamp, ttl=ttl)
        else:
            raise RuntimeError("File already exists.")
        self._backup(timestamp)
    
    def file_get_at(self, timestamp: int, name: str) -> int:
        if name in self.files and self._is_alive(timestamp, name):
            return self.files[name].size
        return None
    
    def file_copy_at(self, timestamp: int, source: str, dest: str) -> None:
        if source in self.files and self._is_alive(timestamp, source):
            self.files[dest] = deepcopy(self.files[source])
            self.files[dest].name = dest
            self.files[dest].timestamp = timestamp
        else:
            raise RuntimeError("Source file does not exist or is dead.")
        self._backup(timestamp)

    def file_search_at(self, timestamp: int, prefix: str):
        sorted_files = sorted(self.files.items(), key=lambda f:(-f[1].size, f[1].name))
        top_10 = []
        for file in sorted_files:
            if len(top_10) >= 10:
                break
            if file[1].name.startswith(prefix) and self._is_alive(timestamp, file[0]):
                top_10.append(file[1].name)
        return top_10

    def rollback(self, timestamp: int) -> None:
        sorted_backups = sorted(self.backups)
        backed_up = False
        for backup in sorted_backups:
            if timestamp >= backup:
                self.files = deepcopy(self.backups[backup])
                for file in self.files.items():
                    file[1].timestamp = timestamp
                backed_up = True
        if not backed_up:
            self.files = {}

simulate_coding_framework = make_simulator(FileStorage)
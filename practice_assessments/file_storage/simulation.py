from __future__ import annotations

from typing import Optional

from framework.simulator import make_simulator


class FileStorage:
    def dummy(self):
        pass


simulate_coding_framework = make_simulator(FileStorage)
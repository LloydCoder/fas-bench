# fmt: off
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ResourceScheduler:
    max_workers: int
    total_cpus: float
    total_memory_bytes: int
    active_workers: int = 0
    active_cpus: float = 0.0
    active_memory_bytes: int = 0

    def __post_init__(self):
        if self.max_workers < 1 or self.total_cpus <= 0 or self.total_memory_bytes <= 0:
            raise ValueError("invalid scheduler capacity")

    def admit(self, cpus: float, memory_bytes: int) -> bool:
        if self.active_workers >= self.max_workers:
            return False
        if self.active_cpus + cpus > self.total_cpus:
            return False
        if self.active_memory_bytes + memory_bytes > self.total_memory_bytes:
            return False
        self.active_workers += 1
        self.active_cpus += cpus
        self.active_memory_bytes += memory_bytes
        return True

    def release(self, cpus: float, memory_bytes: int) -> None:
        if self.active_workers <= 0:
            raise RuntimeError("scheduler release without admission")
        self.active_workers -= 1
        self.active_cpus -= cpus
        self.active_memory_bytes -= memory_bytes

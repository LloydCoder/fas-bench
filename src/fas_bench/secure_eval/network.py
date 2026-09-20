# fmt: off
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class NetworkRule:
    destination: str
    protocol: str
    port: int
    purpose: str

@dataclass(frozen=True)
class NetworkPolicy:
    mode: str = "deny"
    allowlist: tuple[NetworkRule, ...] = ()

    def validate(self) -> None:
        if self.mode not in {"deny", "restricted"}:
            raise ValueError("invalid network policy mode")
        for rule in self.allowlist:
            if not rule.destination or rule.protocol not in {"tcp", "udp"} or not 1 <= rule.port <= 65535 or not rule.purpose:
                raise ValueError("invalid network rule")
        if self.mode == "deny" and self.allowlist:
            raise ValueError("deny mode cannot contain an allowlist")

    def docker_network_mode(self) -> str:
        self.validate()
        if self.mode != "deny":
            raise NotImplementedError("restricted network provider is not implemented in Phase 9 v0.1")
        return "none"

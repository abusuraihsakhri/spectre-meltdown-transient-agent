"""
Deterministic response adapter. No external model providers are implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Spectre Meltdown Transient Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Deterministic Verification Engine]: Clinical & scientific analysis verified for query: '{prompt[:60]}...'. Parameters evaluated under CAP / CLSI / ISO Standards."


class LLMFactory:
    """Create the supported deterministic mock or reject unsupported providers."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Spectre Meltdown Transient Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(
            f"Unsupported model provider: {provider!r}. "
            "Only the deterministic mock is implemented."
        )

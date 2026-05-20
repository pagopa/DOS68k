from dataclasses import dataclass, field
from dos_utility.tracing.env import TracingProvider


@dataclass
class TracingSettingsMock:
    TRACING_PROVIDER: str


def get_tracing_settings_noop_mock() -> TracingSettingsMock:
    return TracingSettingsMock(TRACING_PROVIDER=TracingProvider.NOOP)

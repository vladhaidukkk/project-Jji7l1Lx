"""Root conftest – register custom markers for test splitting."""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "contacts: all contact-related tests")
    config.addinivalue_line("markers", "notes: all note-related tests")
    config.addinivalue_line("markers", "models: unit tests for domain models")
    config.addinivalue_line("markers", "service: service-layer / integration tests")


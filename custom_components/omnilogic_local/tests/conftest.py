"""Common fixtures for the OmniLogic Local tests."""

from collections.abc import Generator
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from unittest.mock import AsyncMock


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch("homeassistant.components.omnilogic_local.async_setup_entry", return_value=True) as mock_setup_entry:
        yield mock_setup_entry

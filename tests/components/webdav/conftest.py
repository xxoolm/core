"""Common fixtures for the WebDAV tests."""

from collections.abc import AsyncIterator, Generator
from json import dumps
from unittest.mock import AsyncMock, patch

from aiowebdav2 import Property, PropertyRequest
import pytest

from homeassistant.components.webdav.const import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_URL, CONF_USERNAME

from .const import (
    BACKUP_METADATA,
    MOCK_GET_PROPERTY_BACKUP_ID,
    MOCK_GET_PROPERTY_METADATA_VERSION,
    MOCK_LIST_WITH_INFOS,
)

from tests.common import MockConfigEntry


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.webdav.async_setup_entry", return_value=True
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="user@webdav.demo",
        domain=DOMAIN,
        data={
            CONF_URL: "https://webdav.demo",
            CONF_USERNAME: "user",
            CONF_PASSWORD: "supersecretpassword",
        },
        entry_id="01JKXV07ASC62D620DGYNG2R8H",
    )


def _get_property(path: str, request: PropertyRequest) -> Property:
    """Return the property of a file."""
    if path.endswith(".json") and request.name == "metadata_version":
        return MOCK_GET_PROPERTY_METADATA_VERSION

    return MOCK_GET_PROPERTY_BACKUP_ID


async def _download_mock(path: str, timeout=None) -> AsyncIterator[bytes]:
    """Mock the download function."""
    if path.endswith(".json"):
        yield dumps(BACKUP_METADATA).encode()

    yield b"backup data"


@pytest.fixture(name="webdav_client")
def mock_webdav_client() -> Generator[AsyncMock]:
    """Mock the aiowebdav client."""
    with (
        patch(
            "homeassistant.components.webdav.helpers.Client",
            autospec=True,
        ) as mock_webdav_client,
    ):
        mock = mock_webdav_client.return_value
        mock.check.return_value = True
        mock.mkdir.return_value = True
        mock.list_with_infos.return_value = MOCK_LIST_WITH_INFOS
        mock.download_iter.side_effect = _download_mock
        mock.upload_iter.return_value = None
        mock.clean.return_value = None
        mock.get_property.side_effect = _get_property
        yield mock

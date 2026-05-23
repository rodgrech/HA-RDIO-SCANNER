"""Data update coordinator for Rdio Scanner."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RdioScannerClient, RdioScannerClientError, RdioScannerData
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RdioScannerDataUpdateCoordinator(DataUpdateCoordinator[RdioScannerData]):
    """Coordinate updates for Rdio Scanner."""

    def __init__(
        self, hass: HomeAssistant, client: RdioScannerClient, scan_interval: int
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> RdioScannerData:
        """Fetch data from Rdio Scanner."""
        try:
            return await self.client.async_get_data()
        except RdioScannerClientError as err:
            raise UpdateFailed("Unable to update Rdio Scanner data") from err

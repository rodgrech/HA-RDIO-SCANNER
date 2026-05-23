"""Client for local Rdio Scanner data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession


class RdioScannerClientError(Exception):
    """Raised when Rdio Scanner cannot be queried."""


@dataclass(slots=True)
class RdioScannerData:
    """Normalized Rdio Scanner data."""

    connected: bool
    url: str
    branding: str | None = None
    email: str | None = None
    systems_count: int | None = None
    talkgroups_count: int | None = None
    groups_count: int | None = None
    tags_count: int | None = None
    admin_configured: bool = False
    raw_config: dict[str, Any] | None = None


class RdioScannerClient:
    """Fetch Rdio Scanner information from supported HTTP endpoints."""

    def __init__(
        self, session: ClientSession, base_url: str, admin_password: str | None = None
    ) -> None:
        """Initialize the client."""
        self._session = session
        self._base_url = normalize_url(base_url)
        self._admin_password = admin_password
        self._token: str | None = None

    async def async_get_data(self) -> RdioScannerData:
        """Fetch and normalize Rdio Scanner data."""
        await self._async_probe_root()

        config: dict[str, Any] | None = None
        if self._admin_password:
            config = await self._async_fetch_admin_config()

        return _normalize(self._base_url, config, bool(self._admin_password))

    async def async_test_connection(self) -> None:
        """Validate that Rdio Scanner can be reached."""
        await self._async_probe_root()
        if self._admin_password:
            await self._async_fetch_admin_config()

    async def _async_probe_root(self) -> None:
        """Check that the web UI is reachable."""
        try:
            async with self._session.get(self._base_url, timeout=10) as response:
                response.raise_for_status()
        except (ClientError, TimeoutError) as err:
            raise RdioScannerClientError from err

    async def _async_fetch_admin_config(self) -> dict[str, Any]:
        """Fetch admin config using Rdio Scanner's supported HTTP admin API."""
        await self._async_login()

        try:
            return await self._async_get_config()
        except ClientResponseError as err:
            if err.status != 401:
                raise RdioScannerClientError from err

            self._token = None
            await self._async_login()
            return await self._async_get_config()
        except (ClientError, TimeoutError, ValueError) as err:
            raise RdioScannerClientError from err

    async def _async_login(self) -> None:
        """Log in to the admin API and cache the session token."""
        if self._token:
            return

        try:
            async with self._session.post(
                f"{self._base_url}/api/admin/login",
                json={"password": self._admin_password},
                timeout=10,
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise RdioScannerClientError from err

        token = data.get("token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token:
            raise RdioScannerClientError("Rdio Scanner admin login returned no token")

        self._token = token

    async def _async_get_config(self) -> dict[str, Any]:
        """Read the admin config payload."""
        headers = {"Authorization": self._token or ""}
        async with self._session.get(
            f"{self._base_url}/api/admin/config", headers=headers, timeout=10
        ) as response:
            response.raise_for_status()
            data = await response.json(content_type=None)

        config = data.get("config") if isinstance(data, dict) else None
        if not isinstance(config, dict):
            raise RdioScannerClientError("Rdio Scanner admin config was not returned")

        return config


def normalize_url(url: str) -> str:
    """Normalize a user-entered Rdio Scanner URL."""
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


def _normalize(
    base_url: str, config: dict[str, Any] | None, admin_configured: bool
) -> RdioScannerData:
    """Normalize config data into entity fields."""
    systems = config.get("systems") if config else None
    groups_data = config.get("groupsData") if config else None
    tags_data = config.get("tagsData") if config else None

    return RdioScannerData(
        connected=True,
        url=base_url,
        branding=_as_str(config.get("branding")) if config else None,
        email=_as_str(config.get("email")) if config else None,
        systems_count=len(systems) if isinstance(systems, list) else None,
        talkgroups_count=_count_talkgroups(systems),
        groups_count=len(groups_data) if isinstance(groups_data, list) else None,
        tags_count=len(tags_data) if isinstance(tags_data, list) else None,
        admin_configured=admin_configured,
        raw_config=config,
    )


def _count_talkgroups(systems: Any) -> int | None:
    """Count configured talkgroups from a Rdio Scanner systems list."""
    if not isinstance(systems, list):
        return None

    total = 0
    for system in systems:
        if isinstance(system, dict) and isinstance(system.get("talkgroups"), list):
            total += len(system["talkgroups"])

    return total


def _as_str(value: Any) -> str | None:
    """Return a non-empty string or None."""
    if value is None:
        return None

    text = str(value).strip()
    return text or None

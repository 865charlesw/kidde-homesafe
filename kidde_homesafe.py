from enum import StrEnum, auto
from dataclasses import dataclass
from typing import Optional, Any, Literal

import aiohttp


_API_PREFIX = "https://api.homesafe.kidde.com/api/v4"


def _dict_by_ids(items: list[dict]) -> dict[int, dict]:
    """Create a dictionary from a list of items, keyed by ID."""
    return {item["id"]: item for item in items}


class KiddeCommand(StrEnum):
    """Known device commands."""

    IDENTIFY = auto()
    IDENTIFYCANCEL = auto()
    TEST = auto()
    HUSH = auto()


class KiddeClientAuthError(Exception):
    """Exception to indicate an authentication error."""


@dataclass(frozen=True)
class KiddeDataset:

    locations: dict[int, dict[str, Any]]
    devices: Optional[dict[int, dict[str, Any]]]
    events: Optional[dict[int, dict[str, Any]]]


class KiddeClient:
    """API Client for Kidde HomeSafe."""

    def __init__(self, cookies: dict[str, str]) -> None:
        """Initialize client."""
        self.cookies = cookies

    @classmethod
    async def from_login(cls, email: str, password: str) -> "KiddeClient":
        """Create a client from a login."""
        url = f"{_API_PREFIX}/auth/login"
        payload = {"email": email, "password": password}
        async with aiohttp.request("POST", url, json=payload) as response:
            if response.status == 403:
                raise KiddeClientAuthError
            response.raise_for_status()
            cookies = {c.key: c.value for c in response.cookies.values()}
            return cls(cookies)

    async def _request(self, path: str, method: Literal["GET", "POST"] = "GET") -> Any:
        """Make a request.

        Parameters
        ----------
        path : str
            Path to request.
        method : str, optional
            HTTP method, by default "GET"

        Returns
        -------
        Any
            Response JSON data.
        """
        url = f"{_API_PREFIX}/{path}"
        async with aiohttp.request(method, url, cookies=self.cookies) as response:
            if response.status == 403:
                raise KiddeClientAuthError
            response.raise_for_status()
            if response.status == 204:
                return None
            return await response.json()

    async def get_data(
        self, get_devices: bool = True, get_events: bool = True
    ) -> "KiddeDataset":
        """Refresh the dataset.

        Parameters
        ----------
        get_devices : bool, optional
            Whether to get devices, by default True
        get_events : bool, optional
            Whether to get events, by default True

        Returns
        -------
        KiddeDataset
            Dataset of locations, devices, and events.
        """
        location_list = await self._request("location")
        locations = _dict_by_ids(location_list)
        devices = {} if get_devices else None
        events = {} if get_events else None
        for location_id in locations:
            if get_devices:
                device_list = await self._request(f"location/{location_id}/device")
                devices.update(_dict_by_ids(device_list))
            if get_events:
                events_result = await self._request(f"location/{location_id}/event")
                events.update(_dict_by_ids(events_result["events"]))
        return KiddeDataset(locations, devices, events)

    async def device_command(
        self, location_id: int, device_id: int, command: KiddeCommand
    ) -> None:
        """Send a command to a device.

        Parameters
        ----------
        location_id : int
            Location ID.
        device_id : int
            Device ID.
        command : KiddeCommand
            Command to send.
        """
        await self._request(
            f"location/{location_id}/device/{device_id}/{command}", "POST"
        )

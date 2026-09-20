"""Provider boundaries for geographic display only; never part of motion authority."""
from __future__ import annotations

import json
from math import isfinite
from typing import Protocol
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

from pydantic import BaseModel, Field, field_validator


class LocationPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    @field_validator("latitude", "longitude")
    @classmethod
    def finite(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("location must be finite")
        return value


class AddressHierarchy(BaseModel):
    provider: str
    country: str | None = None
    state: str | None = None
    district: str | None = None
    city: str | None = None
    locality: str | None = None
    road: str | None = None
    display_name: str | None = None


class ReverseGeocodeRequest(LocationPoint):
    pass


class RouteRequest(BaseModel):
    start: LocationPoint
    destination: LocationPoint


class RouteResult(BaseModel):
    provider: str
    distance_m: float = Field(ge=0)
    duration_s: float = Field(ge=0)
    coordinates: list[tuple[float, float]]  # [longitude, latitude]
    instructions: list[str]


class ProviderUnavailable(RuntimeError):
    pass


def validated_provider_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("provider URL must be an absolute http(s) URL")
    return value.rstrip("/")


class ReverseGeocoder(Protocol):
    def reverse(self, point: LocationPoint) -> AddressHierarchy: ...


class RouteProvider(Protocol):
    def route(self, request: RouteRequest) -> RouteResult: ...


class DisabledReverseGeocoder:
    def reverse(self, point: LocationPoint) -> AddressHierarchy:
        raise ProviderUnavailable("REVERSE GEOCODING SERVICE UNAVAILABLE")


class DisabledRouteProvider:
    def route(self, request: RouteRequest) -> RouteResult:
        raise ProviderUnavailable("ROUTING SERVICE UNAVAILABLE")


class NominatimReverseGeocoder:
    """Optional server-side Nominatim-compatible adapter; no browser key exposure."""
    def __init__(self, base_url: str, timeout_s: float = 4.0):
        self.base_url, self.timeout_s = validated_provider_url(base_url), timeout_s

    def reverse(self, point: LocationPoint) -> AddressHierarchy:
        query = urlencode({"format": "jsonv2", "lat": point.latitude, "lon": point.longitude, "addressdetails": 1})
        request = Request(f"{self.base_url}/reverse?{query}", headers={"User-Agent": "TARK-SIH26007-research-prototype/1.0"})
        try:
            with urlopen(request, timeout=self.timeout_s) as response:
                if response.status != 200:
                    raise ProviderUnavailable("REVERSE GEOCODING SERVICE UNAVAILABLE")
                payload = json.loads(response.read())
        except (OSError, TimeoutError, ValueError) as error:
            raise ProviderUnavailable("REVERSE GEOCODING SERVICE UNAVAILABLE") from error
        address = payload.get("address", {}) if isinstance(payload, dict) else {}
        return AddressHierarchy(provider="NOMINATIM", country=address.get("country"), state=address.get("state") or address.get("region"), district=address.get("state_district") or address.get("county"), city=address.get("city") or address.get("town") or address.get("village"), locality=address.get("suburb") or address.get("neighbourhood"), road=address.get("road"), display_name=payload.get("display_name"))


class OSRMRouteProvider:
    """Optional OSRM-compatible route adapter. No route is synthesized on failure."""
    def __init__(self, base_url: str, timeout_s: float = 5.0):
        self.base_url, self.timeout_s = validated_provider_url(base_url), timeout_s

    def route(self, request: RouteRequest) -> RouteResult:
        points = f"{request.start.longitude},{request.start.latitude};{request.destination.longitude},{request.destination.latitude}"
        url = f"{self.base_url}/route/v1/driving/{points}?{urlencode({'overview':'full','geometries':'geojson','steps':'true'})}"
        try:
            with urlopen(Request(url, headers={"User-Agent": "TARK-SIH26007-research-prototype/1.0"}), timeout=self.timeout_s) as response:
                payload = json.loads(response.read())
        except (OSError, TimeoutError, ValueError) as error:
            raise ProviderUnavailable("ROUTING SERVICE UNAVAILABLE") from error
        routes = payload.get("routes") if isinstance(payload, dict) else None
        if not isinstance(routes, list) or not routes:
            raise ProviderUnavailable("ROUTING SERVICE UNAVAILABLE")
        route = routes[0]
        geometry = route.get("geometry", {}).get("coordinates", [])
        if not isinstance(geometry, list) or not geometry:
            raise ProviderUnavailable("ROUTING SERVICE UNAVAILABLE")
        instructions = [step.get("name") or step.get("maneuver", {}).get("type", "Continue") for leg in route.get("legs", []) for step in leg.get("steps", [])]
        return RouteResult(provider="OSRM", distance_m=float(route.get("distance", 0)), duration_s=float(route.get("duration", 0)), coordinates=[tuple(point) for point in geometry], instructions=instructions)

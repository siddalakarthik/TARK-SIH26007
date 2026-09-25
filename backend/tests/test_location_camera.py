from fastapi.testclient import TestClient

from app.location import AddressHierarchy, LocationPoint, RouteResult
from app.main import create_app


class FakeGeocoder:
    def reverse(self, point: LocationPoint) -> AddressHierarchy:
        return AddressHierarchy(provider="TEST", country="India", state="Telangana", district="Test District", city="Test City", road="Test Road")


class FakeRouter:
    def route(self, request):
        return RouteResult(provider="TEST", distance_m=1200, duration_s=180, coordinates=[(request.start.longitude, request.start.latitude), (request.destination.longitude, request.destination.latitude)], instructions=["Continue", "Arrive"])


def test_vehicle_location_contract_is_distinct_and_uses_labelled_software_simulation():
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/vehicle-location")
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "ONLINE"
    assert payload["location"]["source"] == "SIMULATION"
    assert payload["location"]["quality"] == "SIMULATION"
    assert payload["breadcrumbs"][0]["source"] == "SIMULATION"


def test_reverse_geocoding_and_routing_are_provider_boundaries_not_fabricated_defaults():
    app = create_app(); app.state.reverse_geocoder = FakeGeocoder(); app.state.route_provider = FakeRouter()
    client = TestClient(app)
    address = client.post("/api/v1/location/reverse", json={"latitude": 17.4, "longitude": 78.4})
    route = client.post("/api/v1/routes", json={"start": {"latitude": 17.4, "longitude": 78.4}, "destination": {"latitude": 17.5, "longitude": 78.5}})
    assert address.status_code == 200 and address.json()["country"] == "India"
    assert route.status_code == 200 and route.json()["coordinates"] == [[78.4, 17.4], [78.5, 17.5]]


def test_missing_providers_report_service_unavailable_and_camera_status_has_no_frame_payload():
    client = TestClient(create_app())
    assert client.post("/api/v1/location/reverse", json={"latitude": 17.4, "longitude": 78.4}).status_code == 503
    assert client.post("/api/v1/routes", json={"start": {"latitude": 17.4, "longitude": 78.4}, "destination": {"latitude": 17.5, "longitude": 78.5}}).status_code == 503
    camera = client.get("/api/v1/cameras/vehicle-rgb").json()
    assert camera["state"] == "NOT_CONNECTED" and camera["stream_url"] is None
    assert client.get("/api/v1/cameras/vehicle-rgb/stream").status_code == 503

import pytest
from hypothesis import given, strategies as st
from fastapi.testclient import TestClient
from src.main import app
from src.api.v1.schemas import APIResponse

client = TestClient(app)

@pytest.mark.unit
def test_api_response_envelope_structure():
    """Verify that APIResponse structure is as expected."""
    response = APIResponse(status="success", data={"test": 1}, error=None)
    assert response.status == "success"
    assert response.data == {"test": 1}
    assert response.error is None

@pytest.mark.parametrize("endpoint", [
    "/api/v1/health",
    "/api/v1/health/ready"
])
def test_health_endpoints_envelope(endpoint):
    """Verify that public health endpoints use the envelope."""
    response = client.get(endpoint)
    json_data = response.json()
    assert "status" in json_data
    assert "data" in json_data
    assert "error" in json_data

@given(st.text())
def test_api_response_generic(data):
    """Property: APIResponse should handle any data type."""
    resp = APIResponse(data=data)
    assert resp.data == data
    assert resp.status == "success"

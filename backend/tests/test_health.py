def test_health_check(client):
    """Test health endpoint returns 200 and healthy database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["service"] == "INDUSAI-X Backend"

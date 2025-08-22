def test_read_root(client):
    """
    Test root endpoint
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "HR Internal Q&A System API"


def test_health_check(client):
    """
    Test health check endpoint
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
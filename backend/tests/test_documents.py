def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Document Q&A Platform" in response.json()["message"]


def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepass123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_register_duplicate_user(client):
    client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "pass123"
    })
    response = client.post("/api/auth/register", json={
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "pass123"
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "pass123"
    })
    response = client.post("/api/auth/login", data={
        "username": "loginuser",
        "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_list_documents_unauthorized(client):
    response = client.get("/api/documents/")
    assert response.status_code == 401


def test_list_documents_empty(client, auth_headers):
    response = client.get("/api/documents/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_upload_invalid_file_type(client, auth_headers):
    response = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("test.exe", b"fake content", "application/x-msdownload")}
    )
    assert response.status_code == 400
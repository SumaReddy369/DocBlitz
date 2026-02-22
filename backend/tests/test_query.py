def test_query_unauthorized(client):
    response = client.post("/api/query/", json={
        "question": "What is this about?"
    })
    assert response.status_code == 401


def test_query_empty_question(client, auth_headers):
    response = client.post(
        "/api/query/",
        headers=auth_headers,
        json={"question": "   "}
    )
    assert response.status_code == 400


def test_query_history_empty(client, auth_headers):
    response = client.get("/api/query/history", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []
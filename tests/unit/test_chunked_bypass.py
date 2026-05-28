from fastapi.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_chunked_encoding_list():
    headers = {
        "Transfer-Encoding": "gzip, chunked"
    }
    response = client.post("/api/health", headers=headers, json={"status": "ok"})
    assert response.status_code == 411
    assert response.json()["detail"] == "Chunked encoding not supported"

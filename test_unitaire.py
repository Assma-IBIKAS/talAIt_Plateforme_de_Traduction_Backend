import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test Login simple
def test_login():
    response = client.post(
        "/login",
        data={"username": "Assma", "password": "assma"}, 
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200



# Test accès protégé SANS token
def test_protected_without_token():
    response = client.post(
        "/translate",
        json={"text": "Bonjour", "direction": "fr-en"}
    )

    # Un endpoint protégé doit renvoyer 401 Unauthorized
    assert response.status_code == 401

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
resp = client.get('/api/tasks/flow-trend?days=3')
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text[:2000]}")

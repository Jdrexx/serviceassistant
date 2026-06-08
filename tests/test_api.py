from fastapi.testclient import TestClient
from src.main import app
client = TestClient(app)
def test_health():
    r=client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_intake_high_urgency():
    data=client.post('/api/intake', json={'customer_name':'Jane','phone':'555','service_needed':'plumbing','message':'urgent leak today','preferred_time':'now'}).json()
    assert data['urgency'] == 'high'

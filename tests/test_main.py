from starlette.testclient import TestClient
from main import app
from services import create_user

def test_get_home():
    client = TestClient(app)
    res = client.get('/')
    assert res.status_code == 200
    assert 'GCSE Chinese Trainer' in res.text
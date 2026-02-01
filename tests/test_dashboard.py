from starlette.testclient import TestClient
from main import app
from services import create_user
import time

def test_dashboard_content_logged_in():
    client = TestClient(app)
    unique_email = f"dashboard_test_{int(time.time())}@example.com"
    password = "password123"
    
    # Create user
    create_user(unique_email, password)
    
    # Login
    res = client.post('/login', data={'email': unique_email, 'password': password}, follow_redirects=False)
    assert res.status_code == 303
    
    # Get Dashboard
    res = client.get('/')
    assert res.status_code == 200
    assert "Review History" in res.text
    assert "/review" in res.text
    assert "Start Practice" in res.text
    assert "Profile" in res.text

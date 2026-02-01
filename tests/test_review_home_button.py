from starlette.testclient import TestClient
from main import app
from services import create_user
import time

def test_review_page_home_button():
    client = TestClient(app)
    unique_email = f"review_home_test_{int(time.time())}@example.com"
    password = "password123"
    
    # Create user
    create_user(unique_email, password)
    
    # Login
    client.post('/login', data={'email': unique_email, 'password': password}, follow_redirects=False)
    
    # Get Review Page
    res = client.get('/review')
    assert res.status_code == 200
    assert "Back to Dashboard" in res.text
    assert 'href="/"' in res.text

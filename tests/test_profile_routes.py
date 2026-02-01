from starlette.testclient import TestClient
from main import app
from services import create_user
from models import users, get_user_by_email
import pytest
import time

@pytest.fixture
def client():
    return TestClient(app)

def test_profile_access_and_update(client):
    unique_email = f"profile_test_{int(time.time())}@example.com"
    password = "initialPassword123"
    new_password = "newPassword456"
    
    # Create user
    user = create_user(unique_email, password)
    assert user is not None
    
    # Verify DB insertion
    db_user = get_user_by_email(unique_email)
    assert db_user is not None
    
    # 1. Login to get session
    # Force no redirect following to check for 303
    res = client.post('/login', data={'email': unique_email, 'password': password}, follow_redirects=False)
    
    if res.status_code != 303:
        # If it didn't redirect, it likely failed.
        print(f"Login Response: {res.text}")
        
    assert res.status_code == 303 
    
    # 2. Access Profile Page (manual redirect following not needed as client maintains cookie jar, but next request is separate)
    res = client.get('/profile')
    assert res.status_code == 200
    assert unique_email in res.text
    assert 'Current Password' in res.text
    
    # 3. Update Password - Fail (Mismatch)
    res = client.post('/profile', data={
        'old_password': password,
        'new_password': new_password,
        'confirm_password': "mismatchPassword"
    })
    assert "New passwords do not match" in res.text
    
    # 4. Update Password - Fail (Wrong Old Password)
    res = client.post('/profile', data={
        'old_password': "wrongPassword",
        'new_password': new_password,
        'confirm_password': new_password
    })
    assert "Incorrect current password" in res.text
    
    # 5. Update Password - Success
    res = client.post('/profile', data={
        'old_password': password,
        'new_password': new_password,
        'confirm_password': new_password
    })
    assert "Password updated successfully" in res.text
    
    # 6. Verify Login with new password
    client.get('/logout') # Clear session
    
    # Old password should fail (returns 200 with "Login Failed")
    res = client.post('/login', data={'email': unique_email, 'password': password}, follow_redirects=False)
    assert res.status_code == 200
    assert "Login Failed" in res.text
    
    # New password should succeed
    res = client.post('/login', data={'email': unique_email, 'password': new_password}, follow_redirects=False)
    assert res.status_code == 303
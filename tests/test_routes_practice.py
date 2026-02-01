from starlette.testclient import TestClient
from main import app
from services import create_user
from models import create_question, sessions

client = TestClient(app)

def test_practice_routes():
    # Setup
    user = create_user("route_test@test.com", "pass")
    q = create_question(theme="Route Test Q", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")
    
    # Login to get session cookie (mocking session is harder with TestClient, 
    # so we might need to rely on the fact that FastHTML sessions are cookie-based)
    # Alternatively, we just test the redirects if not logged in.
    
    # 1. Unauthenticated Access -> Redirect
    res = client.get('/practice', follow_redirects=False)
    assert res.status_code == 303
    assert res.headers['location'] == '/login'

    # 2. Authenticated Access
    # Simulate login
    client.post('/login', data={'email': "route_test@test.com", 'password': "pass"})
    
    # List
    res = client.get('/practice')
    assert res.status_code == 200
    assert "Route Test Q" in res.text

    # Prep
    res = client.get(f'/practice/{q.id}/prep')
    assert res.status_code == 200
    assert "Preparation Time" in res.text
    assert "Q1" in res.text

    # Exam
    res = client.get(f'/practice/{q.id}/exam')
    assert res.status_code == 200
    assert "Exam In Progress" in res.text

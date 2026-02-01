from starlette.testclient import TestClient
from main import app
from services import create_user
from models import create_question, create_practice_session, submit_answer

client = TestClient(app)

import time

def test_review_routes():
    # Setup
    unique_email = f"review_test_{int(time.time())}@test.com"
    user = create_user(unique_email, "pass")
    q = create_question(theme="Review Q", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")
    session = create_practice_session(user.id, q.id)
    submit_answer(session.id, 1, "/audio.webm")

    # Login
    client.post('/login', data={'email': unique_email, 'password': "pass"})

    # 1. List Sessions
    res = client.get('/review')
    assert res.status_code == 200
    assert "Review Q" in res.text

    # 2. Session Detail
    res = client.get(f'/review/{session.id}')
    assert res.status_code == 200
    assert "Transcripts" in res.text
    # Check if answer logic is present (though difficult to check exact content without seed)

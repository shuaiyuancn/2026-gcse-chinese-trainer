from main import create_question, create_practice_session, get_practice_session, submit_answer, create_user
from datetime import datetime

def test_practice_workflow():
    # Setup Data
    user = create_user("practice@test.com", "pass")
    q = create_question(theme="P1", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")

    # 1. Start Session
    session = create_practice_session(user.id, q.id)
    assert session.id is not None
    assert session.user_id == user.id
    assert session.question_id == q.id
    
    # 2. Retrieve Session
    fetched_session = get_practice_session(session.id)
    assert fetched_session is not None

    # 3. Submit Answer
    ans = submit_answer(
        session_id=session.id,
        question_number=1,
        audio_url="/uploads/audio1.mp3"
    )
    assert ans.id is not None
    assert ans.session_id == session.id
    assert ans.question_number == 1
    assert ans.audio_url == "/uploads/audio1.mp3"

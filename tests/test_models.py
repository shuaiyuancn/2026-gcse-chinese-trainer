from models import User, Question, PracticeSession, Answer
from datetime import datetime

def test_user_model_structure():
    # This test just checks if we can instantiate the model with expected fields
    user = User(
        email="test@example.com",
        password_hash="hashed_secret",
        role="student"
    )
    assert user.email == "test@example.com"
    assert user.role == "student"

def test_question_model_structure():
    q = Question(
        theme="Test Card",
        image_url="/img/test.jpg",
        question_1="Q1",
        question_2="Q2",
        question_3="Q3",
        question_4="Q4",
        question_5="Q5",
        topic="Theme 1"
    )
    assert q.theme == "Test Card"
    assert q.question_1 == "Q1"

def test_practice_session_model():
    session = PracticeSession(
        user_id=1,
        question_id=1,
        date_taken=datetime.now(),
        total_score=0
    )
    assert session.user_id == 1

def test_answer_model():
    ans = Answer(
        session_id=1,
        question_number=1,
        audio_url="/audio/1.mp3",
        transcript="ni hao",
        ai_feedback="Good",
        score=5
    )
    assert ans.transcript == "ni hao"

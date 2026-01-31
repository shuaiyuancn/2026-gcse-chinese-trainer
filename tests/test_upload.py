from starlette.testclient import TestClient
from main import app, create_question, create_user, create_practice_session
import io

client = TestClient(app)

def test_audio_upload_route():
    # Setup
    user = create_user("upload_test@test.com", "pass")
    q = create_question(title="Upload Q", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")
    session = create_practice_session(user.id, q.id)

    # Create dummy audio file
    audio_content = b"fake audio content"
    audio_file = io.BytesIO(audio_content)
    
    # Simulate Upload
    # Note: Authentication logic might interfere if the route expects a session,
    # but the current implementation of the upload route doesn't explicit check session 
    # (it takes session_id as path param).
    
    res = client.post(
        f"/practice/{session.id}/answer/1",
        files={"audio_file": ("test.webm", audio_file, "audio/webm")}
    )
    
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "answer_id" in data

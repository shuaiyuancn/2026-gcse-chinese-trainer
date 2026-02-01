from unittest.mock import patch, MagicMock
from main import process_audio_with_ai, answers, Answer, create_question, create_practice_session, submit_answer, create_user
import os

def test_process_audio_with_ai():
    # Setup DB data
    # We need a valid answer ID to update
    user = create_user("ai_test@test.com", "pass")
    q = create_question(theme="AI Q", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")
    session = create_practice_session(user.id, q.id)
    ans = submit_answer(session.id, 1, "dummy_path.webm")
    
    # Mock Environment Variable
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        # Mock genai
        with patch("main.genai") as mock_genai:
            # Setup Mock Response
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = '{"transcript": "Ni Hao", "feedback": "Good job", "score": 5}'
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Run Function
            process_audio_with_ai(ans.id, "dummy_path.webm", "Question Text")
            
            # Verify Calls
            mock_genai.configure.assert_called_with(api_key="fake_key")
            mock_genai.upload_file.assert_called_with("dummy_path.webm")
            mock_model.generate_content.assert_called()
            
            # Verify DB Update
            updated_ans = answers[ans.id]
            assert updated_ans.transcript == "Ni Hao"
            assert updated_ans.ai_feedback == "Good job"
            assert updated_ans.score == 5

def test_process_audio_no_key():
    # Ensure it handles missing key gracefully
    with patch.dict(os.environ, {}, clear=True):
        # We need to make sure GEMINI_API_KEY is definitely NOT present.
        # However, patch.dict with clear=True clears ALL env vars which might break DB config.
        # Safer to just ensure GEMINI_API_KEY is popped.
        with patch.dict(os.environ):
            if "GEMINI_API_KEY" in os.environ:
                del os.environ["GEMINI_API_KEY"]
                
            process_audio_with_ai(999, "path", "text")
            # Should print error and return, no exception raised

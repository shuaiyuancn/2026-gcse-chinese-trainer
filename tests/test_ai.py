from unittest.mock import patch, MagicMock, ANY
from services import process_audio_with_ai, run_ai_feedback_task, create_user
from models import create_question, create_practice_session, submit_answer, answers
import os

def test_ai_processing_logic():
    # This tests the actual worker logic (synchronous)
    
    # Setup DB data
    user = create_user("ai_test@test.com", "pass")
    q = create_question(theme="AI Q", image_url="/img.jpg", question_1="Q1", question_2="Q2", question_3="Q3", question_4="Q4", question_5="Q5", topic="T1")
    session = create_practice_session(user.id, q.id)
    ans = submit_answer(session.id, 1, "dummy_path.webm")
    
    # Mock Environment Variable
    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        # Mock genai Client
        with patch("services.genai.Client") as MockClient:
            mock_client_instance = MockClient.return_value
            
            # Setup Mock Response
            mock_response = MagicMock()
            mock_response.text = '{"transcript": "Ni Hao", "feedback": "Good job", "score": 5}'
            mock_client_instance.models.generate_content.return_value = mock_response
            
            # Mock Path read_bytes
            with patch("services.pathlib.Path") as MockPath:
                mock_path_instance = MockPath.return_value
                mock_path_instance.exists.return_value = True
                mock_path_instance.read_bytes.return_value = b"fake_audio_bytes"
                
                # Run Worker Function directly
                run_ai_feedback_task(ans.id, "dummy_path.webm", "Question Text")
                
                # Verify Calls
                MockClient.assert_called_with(api_key="fake_key")
                # Ensure generate_content was called
                mock_client_instance.models.generate_content.assert_called()
                # Check args - index 0 is contents list
                call_args = mock_client_instance.models.generate_content.call_args
                assert call_args is not None
                # Check model arg
                assert call_args.kwargs['model'] == "gemini-2.5-flash"
                
                # Verify DB Update
                updated_ans = answers[ans.id]
                assert updated_ans.transcript == "Ni Hao"
                assert updated_ans.ai_feedback == "Good job"
                assert updated_ans.score == 5

def test_process_audio_dispatch():
    # This verifies that the main service function offloads to a thread
    with patch("services.threading.Thread") as mock_thread:
        process_audio_with_ai(1, "path", "text")
        
        # Verify it created a thread targeting the worker
        mock_thread.assert_called_once()
        args = mock_thread.call_args[1] if mock_thread.call_args[1] else mock_thread.call_args[0]
        # Depending on how it's called (kwargs or args)
        # We expect target=run_ai_feedback_task
        assert mock_thread.call_args.kwargs['target'] == run_ai_feedback_task
        mock_thread.return_value.start.assert_called_once()

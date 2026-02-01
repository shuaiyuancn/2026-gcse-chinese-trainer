import bcrypt
from google import genai
from google.genai import types
import json
import os
import threading
import time
from datetime import datetime
from models import users, User, answers, Answer, create_user_record

MODEL = "gemini-2.5-flash"

# --- Auth Services ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(email, password, role="student"):
    pwd_hash = hash_password(password)
    return create_user_record(email, pwd_hash, role)

def authenticate_user(email, password):
    # Using the models helper directly or accessing table
    from models import get_user_by_email
    user = get_user_by_email(email)
    if user and verify_password(password, user.password_hash):
        return user
    return None

# --- AI Services ---
def run_ai_feedback_task(answer_id: int, audio_path: str, question_text: str):
    """
    Synchronous worker function that communicates with Gemini API
    and updates the database.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Skipping AI processing: GEMINI_API_KEY not set.")
        return

    try:
        client = genai.Client(api_key=api_key)
        
        # Upload the file
        audio_file = client.files.upload(file=audio_path)
        
        # Wait for file to be active
        while True:
            file_check = client.files.get(name=audio_file.name)
            if file_check.state == "ACTIVE":
                break
            elif file_check.state == "FAILED":
                raise Exception(f"File processing failed: {file_check.uri}")
            print(f"Waiting for file processing... Current state: {file_check.state}")
            time.sleep(1)
        
        prompt = f"""
        You are a GCSE Chinese teacher (Higher Tier).
        The student is answering the question: "{question_text}"
        
        1. Transcribe the audio exactly into Chinese characters.
        2. Provide feedback based on GCSE Higher Tier criteria (Grammar, Vocabulary, Pronunciation/Tones). Note the feedback should be for the original audio, not the transcription.
        3. Give a score out of 5 (integer).
        
        Return ONLY a JSON object with keys: "transcript", "feedback", "score".
        Example: {{ "transcript": "...", "feedback": "...", "score": 3 }}
        """
        
        result = client.models.generate_content(
            model=MODEL,
            contents=[audio_file, prompt]
        )
        response_text = result.text.strip()
        
        # Clean up JSON markdown if present
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        elif response_text.startswith("```"):
            response_text = response_text[3:-3]
        
        data = json.loads(response_text)
        
        # Update Answer Record
        ans = answers[answer_id]
        ans.transcript = data.get("transcript", "")
        ans.ai_feedback = data.get("feedback", "")
        ans.score = data.get("score", 0)
        answers.update(ans)
        
        print(f"AI Processing complete for Answer {answer_id}")
        
    except Exception as e:
        print(f"Error in AI processing: {e}")

def process_audio_with_ai(answer_id: int, audio_path: str, question_text: str):
    """
    Wrapper that launches the AI processing in a background thread.
    """
    thread = threading.Thread(
        target=run_ai_feedback_task, 
        args=(answer_id, audio_path, question_text)
    )
    thread.start()
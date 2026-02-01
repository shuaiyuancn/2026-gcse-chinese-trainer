from fasthtml.common import *
from fastsql import NotFoundError
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core import db

# --- Data Models ---
@dataclass
class User:
    email: str
    password_hash: str
    role: str = "student"
    created_at: datetime = None
    id: int = None

@dataclass
class Question:
    theme: str
    image_url: str
    question_1: str
    question_2: str
    question_3: str
    question_4: str
    question_5: str
    topic: str
    created_at: datetime = None
    id: int = None

@dataclass
class PracticeSession:
    user_id: int
    question_id: int
    date_taken: datetime
    total_score: int = 0
    id: int = None

@dataclass
class Answer:
    session_id: int
    question_number: int
    audio_url: str
    transcript: str = ""
    ai_feedback: str = ""
    score: int = 0
    id: int = None

# Initialize Tables
users = db.create(User)
questions = db.create(Question)
sessions = db.create(PracticeSession)
answers = db.create(Answer)

# --- CRUD Helpers ---

# User
def create_user_record(email, password_hash, role="student"):
    user = User(email=email, password_hash=password_hash, role=role, created_at=datetime.now())
    return users.insert(user)

def get_user_by_email(email):
    rows = list(users.rows_where("email = ?", [email]))
    if rows:
        return User(**rows[0])
    return None

def get_user_by_id(id):
    try:
        return users[id]
    except NotFoundError:
        return None

# Question
def create_question(**kwargs):
    kwargs['created_at'] = datetime.now()
    return questions.insert(Question(**kwargs))

def get_all_questions():
    return questions()

def get_question(id):
    try:
        return questions[id]
    except NotFoundError:
        return None

def update_question(id, **kwargs):
    return questions.update(questions[id], **kwargs)

def delete_question(id):
    questions.delete(id)

# Practice Session
def create_practice_session(user_id, question_id):
    session = PracticeSession(user_id=user_id, question_id=question_id, date_taken=datetime.now())
    return sessions.insert(session)

def get_practice_session(id):
    try:
        return sessions[id]
    except NotFoundError:
        return None

def get_user_sessions(user_id):
    return sessions.rows_where("user_id = ? ORDER BY date_taken DESC", [user_id])

# Answer
def submit_answer(session_id, question_number, audio_url):
    answer = Answer(session_id=session_id, question_number=question_number, audio_url=audio_url)
    return answers.insert(answer)

def get_session_answers(session_id):
    return answers.rows_where("session_id = ? ORDER BY question_number", [session_id])

def update_answer(id, **kwargs):
    return answers.update(answers[id], **kwargs)

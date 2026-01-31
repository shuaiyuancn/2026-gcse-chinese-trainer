from fasthtml.common import *
from fastsql import Database, NotFoundError
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import bcrypt

# --- Database Setup ---
def get_db_url():
    # Priority 1: DATABASE_URL (set in compose.yaml or Vercel)
    url = os.getenv("DATABASE_URL")
    if url: 
        return url.replace("postgres://", "postgresql://")
    
    # Priority 2: Supabase Non-Pooling (Best for SQLAlchemy/FastSQL)
    non_pooling_url = os.getenv("POSTGRES_URL_NON_POOLING")
    if non_pooling_url: 
        return non_pooling_url.replace("postgres://", "postgresql://")

    # Priority 3: Supabase / Postgres env vars
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url: 
        return pg_url.replace("postgres://", "postgresql://")
    
    # Fallback/Default
    return "postgresql://postgres:postgres@localhost:5432/postgres"

db_url = get_db_url()
db = Database(db_url)

# --- Auth Helpers ---
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(email, password, role="student"):
    pwd_hash = hash_password(password)
    user = User(email=email, password_hash=pwd_hash, role=role, created_at=datetime.now())
    return users.insert(user)

def authenticate_user(email, password):
    for row in users.rows_where("email = ?", [email]):
        user = User(**row)
        if verify_password(password, user.password_hash):
            return user
    return None

# --- Question CRUD ---
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

# --- Practice Workflow ---
def create_practice_session(user_id, question_id):
    session = PracticeSession(user_id=user_id, question_id=question_id, date_taken=datetime.now())
    return sessions.insert(session)

def get_practice_session(id):
    try:
        return sessions[id]
    except NotFoundError:
        return None

def submit_answer(session_id, question_number, audio_url):
    answer = Answer(session_id=session_id, question_number=question_number, audio_url=audio_url)
    return answers.insert(answer)

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
    title: str
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
# users, questions, sessions, answers = db.create(User, Question, PracticeSession, Answer)
users = db.create(User)
questions = db.create(Question)
sessions = db.create(PracticeSession)
answers = db.create(Answer)

# --- App Setup ---
app, rt = fast_app(
    hdrs=(Link(rel='stylesheet', href='index.css'),), 
    pico=False,
    secret_key=os.getenv('AUTH_SECRET', 'dev-secret')
)

# --- Auth Routes ---
@rt('/login')
def get():
    return Titled("Login",
        Form(
            Input(name="email", type="email", placeholder="Email", required=True),
            Input(name="password", type="password", placeholder="Password", required=True),
            Button("Login"),
            action="/login", method="post"
        ),
        P(A("Sign Up", href="/signup"))
    )

@rt('/login')
def post(session, email: str, password: str):
    user = authenticate_user(email, password)
    if not user:
        return Titled("Login Failed", 
            P("Invalid email or password."),
            A("Try Again", href="/login")
        )
    session['user_id'] = user.id
    return Redirect('/')

@rt('/signup')
def get():
    return Titled("Sign Up",
        Form(
            Input(name="email", type="email", placeholder="Email", required=True),
            Input(name="password", type="password", placeholder="Password", required=True),
            Button("Sign Up"),
            action="/signup", method="post"
        ),
        P(A("Login", href="/login"))
    )

@rt('/signup')
def post(session, email: str, password: str):
    # TODO: Check if user exists to avoid duplicates/error
    try:
        user = create_user(email, password)
        session['user_id'] = user.id
        return Redirect('/')
    except Exception as e:
        return Titled("Error", P(f"Could not sign up: {e}"), A("Back", href="/signup"))

@rt('/logout')
def get(session):
    session.clear()
    return Redirect('/')

@rt('/')
def get(session):
    user_id = session.get('user_id')
    user = users[user_id] if user_id else None
    
    if user:
        return Titled(f"Welcome, {user.email}",
            Div(
                H2("Dashboard"),
                P("Start your practice session."),
                A("Start Practice", href="/practice", cls="btn"),
                Br(), Br(),
                A("Logout", href="/logout"),
                cls="container"
            )
        )

    return Main(
        Div(
            H1("GCSE Chinese Trainer"),
            P(f"Prepare for your Higher Tier Speaking Exam."),
            Div(
                A("Login", href="/login", cls="btn"),
                " ",
                A("Sign Up", href="/signup", cls="btn secondary"),
            ),
            P(f"Database URL detected: {db_url.split('@')[-1] if '@' in db_url else 'Local/Unknown'}"),
            cls="container"
        )
    )

if __name__ == "__main__":
    serve()
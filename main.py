from fasthtml.common import *
from fastsql import Database, NotFoundError
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import bcrypt
import google.generativeai as genai
import json

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

# --- App Setup ---
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/icon?family=Material+Icons'),
        Link(rel='stylesheet', href='index.css'),
        Script(src='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'),
        Script(src='/public/recorder.js')
    ), 
    pico=False,
    secret_key=os.getenv('AUTH_SECRET', 'dev-secret')
)

# Serve static files from public directory
@rt("/public/{fname:path}")
def get(fname: str):
    return FileResponse(f'public/{fname}')

# --- Practice Routes ---
@rt('/practice')
def get(session):
    if not session.get('user_id'): return Redirect('/login')
    
    qs = get_all_questions()
    return Titled("Select a Topic",
        Div(
            *[
                Card(
                    H3(q.theme),
                    P(f"Topic: {q.topic}"),
                    A("Start Practice", href=f"/practice/{q.id}/prep", cls="btn"),
                    style="margin-bottom: 1rem;"
                ) for q in qs
            ],
            cls="container"
        )
    )

@rt('/practice/{id}/prep')
def get(id: int, session):
    if not session.get('user_id'): return Redirect('/login')
    
    q = get_question(id)
    if not q: return Titled("Error", P("Question not found"))

    # Create session entry if not exists (or handle logic)
    # For now, just show prep screen
    return Titled("Preparation Time",
        Div(
            H2(f"Topic: {q.topic}"),
            Div(
                Img(src=q.image_url, style="max-width: 100%; height: auto;"),
                cls="card"
            ),
            Div(
                H3("Questions (Preparation)"),
                P(f"1. {q.question_1}"),
                P(f"2. {q.question_2}"),
                P(f"3. {q.question_3}"),
                cls="card"
            ),
            Div(
                H4("Time Remaining: 03:00", id="timer"),
                A("Start Exam Now", href=f"/practice/{q.id}/exam", cls="btn"),
                style="margin-top: 1rem;"
            ),
            # Simple script for timer would go here or in external JS
            cls="container"
        )
    )

@rt('/practice/{id}/exam')
def get(id: int, session):
    if not session.get('user_id'): return Redirect('/login')
    
    q = get_question(id)
    if not q: return Titled("Error", P("Question not found"))
    
    # Initialize practice session in DB
    user_id = session['user_id']
    ps = create_practice_session(user_id, q.id)
    
    return Titled("Exam In Progress",
        Div(
            Div(
                Img(src=q.image_url, style="max-width: 100%; height: auto;"),
                style="margin-bottom: 1rem;"
            ),
            Div(
                # Hidden fields for JS to pick up
                Input(type="hidden", id="session_id", value=ps.id),
                Input(type="hidden", id="question_number", value=1),
                
                H3("Question 1"),
                P(q.question_1, cls="question-text", id="question-text"),
                
                # Recording UI
                Div(
                    Button("Start Recording", id="recordBtn", onclick="startRecording()", cls="btn"),
                    Button("Stop & Upload", id="stopBtn", onclick="stopRecording()", cls="btn red", disabled=True),
                    P("Ready to record.", id="status"),
                    cls="recording-controls"
                ),
                
                # Navigation - Logic to be added for next question
                Button("Next Question", cls="btn next-btn", style="margin-top: 1rem;"),
                id="exam-container"
            ),
            cls="container"
        )
    )

# --- AI Integration ---
def process_audio_with_ai(answer_id: int, audio_path: str, question_text: str):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Skipping AI processing: GEMINI_API_KEY not set.")
        return

    try:
        genai.configure(api_key=api_key)
        
        # Upload the file
        audio_file = genai.upload_file(audio_path)
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are a GCSE Chinese teacher (Higher Tier).
        The student is answering the question: "{question_text}"
        
        1. Transcribe the audio exactly into Chinese characters.
        2. Provide feedback based on GCSE Higher Tier criteria (Grammar, Vocabulary, Pronunciation/Tones).
        3. Give a score out of 5 (integer).
        
        Return ONLY a JSON object with keys: "transcript", "feedback", "score".
        Example: {{ "transcript": "...", "feedback": "...", "score": 3 }}
        """
        
        result = model.generate_content([audio_file, prompt])
        response_text = result.text.strip()
        
        # Clean up JSON markdown if present
        if response_text.startswith("```json"):
            response_text = response_text[7:-3]
        
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

@rt('/practice/{session_id}/answer/{question_number}')
async def post(session_id: int, question_number: int, audio_file: UploadFile):
    # Ensure uploads directory exists
    os.makedirs('uploads', exist_ok=True)
    
    file_path = f"uploads/{session_id}_{question_number}_{int(datetime.now().timestamp())}.webm"
    
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())
        
    answer = submit_answer(session_id, question_number, file_path)
    
    # Trigger AI Processing
    try:
        sess = sessions[session_id]
        q = questions[sess.question_id]
        q_text = getattr(q, f"question_{question_number}", "Unknown Question")
        process_audio_with_ai(answer.id, file_path, q_text)
    except Exception as e:
        print(f"Failed to trigger AI: {e}")

    return {"status": "success", "answer_id": answer.id}

# --- Review Routes ---
@rt('/review')
def get(session):
    if not session.get('user_id'): return Redirect('/login')
    
    user_id = session['user_id']
    user_sessions = sessions.rows_where("user_id = ? ORDER BY date_taken DESC", [user_id])
    
    # Enrich with Question Title
    history_items = []
    for row in user_sessions:
        s = PracticeSession(**row)
        q = get_question(s.question_id)
        title = q.theme if q else "Unknown Topic"
        history_items.append(
            Card(
                H4(f"{title}"),
                P(f"Date: {s.date_taken}"),
                A("View Results", href=f"/review/{s.id}", cls="btn"),
                style="margin-bottom: 1rem;"
            )
        )
        
    return Titled("My Practice History",
        Div(
            *history_items if history_items else [P("No practice sessions yet.")],
            cls="container"
        )
    )

@rt('/review/{id}')
def get(id: int, session):
    if not session.get('user_id'): return Redirect('/login')
    
    # Verify ownership
    s = get_practice_session(id)
    if not s or s.user_id != session['user_id']:
        return Titled("Error", P("Session not found or access denied."))
    
    q = get_question(s.question_id)
    session_answers = answers.rows_where("session_id = ? ORDER BY question_number", [id])
    
    return Titled("Session Review",
        Div(
            H2(f"Topic: {q.theme if q else 'Unknown'}"),
            Div(
                Img(src=q.image_url, style="max-width: 100%; height: auto;") if q else "",
                style="margin-bottom: 2rem;"
            ),
            H3("Transcripts & Feedback"),
            Div(
                *[
                    Card(
                        H4(f"Question {Answer(**ans).question_number}"),
                        Audio(src=f"/{Answer(**ans).audio_url}", controls=True),
                        P(B("Transcript: "), Answer(**ans).transcript),
                        P(B("Feedback: "), Answer(**ans).ai_feedback),
                        P(B("Score: "), f"{Answer(**ans).score}/5"),
                        style="margin-bottom: 1rem;"
                    ) for ans in session_answers
                ],
                cls="answers-list"
            ),
            A("Back to History", href="/review", cls="btn secondary"),
            cls="container"
        )
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

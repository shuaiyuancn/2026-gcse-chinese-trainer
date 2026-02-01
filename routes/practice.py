from fasthtml.common import *
from models import get_all_questions, get_question, create_practice_session, submit_answer, sessions, questions
from services import process_audio_with_ai
import json
import os
from datetime import datetime

def setup_practice_routes(rt):
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
        
        questions_json = json.dumps({
            "1": q.question_1,
            "2": q.question_2,
            "3": q.question_3,
            "4": q.question_4,
            "5": q.question_5
        })

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
                    
                    H3("Question 1", id="question-title"),
                    P(q.question_1, cls="question-text", id="question-text"),
                    
                    # Recording UI
                    Div(
                        Button("Start Recording", id="recordBtn", onclick="startRecording()", cls="btn"),
                        Button("Stop & Upload", id="stopBtn", onclick="stopRecording()", cls="btn red", disabled=True),
                        P("Ready to record.", id="status"),
                        cls="recording-controls"
                    ),
                    
                    # Navigation
                    Button("Next Question", id="nextBtn", onclick="nextQuestion()", cls="btn next-btn", style="margin-top: 1rem;", disabled=True),
                    id="exam-container"
                ),
                Script(f"const questionsData = {questions_json};"),
                cls="container"
            )
        )

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

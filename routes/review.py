from fasthtml.common import *
from models import get_question, get_practice_session, sessions, answers, PracticeSession, Answer

def setup_review_routes(rt):
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

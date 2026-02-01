from core import app, rt, db_url
from fasthtml.common import *
from models import users
from routes.auth import setup_auth_routes
from routes.practice import setup_practice_routes
from routes.review import setup_review_routes

import os

# Setup Routes
setup_auth_routes(rt)
setup_practice_routes(rt)
setup_review_routes(rt)

# --- Main Dashboard ---
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
                A("Review History", href="/review", cls="btn teal"),
                Br(), Br(),
                A("Profile", href="/profile", cls="btn blue-grey"),
                Br(), Br(),
                A("Logout", href="/logout", cls="btn red"),
                cls="container"
            )
        )

    return Main(
        Div(
            H1("GCSE Chinese Trainer"),
            P(f"Prepare for your Higher Tier Speaking Exam."),
            Div(
                A("Login", href="/login", cls="btn"),
                Br(), Br(),
                A("Sign Up", href="/signup", cls="btn secondary"),
            ),
            P(f"Database URL detected: {db_url.split('@')[-1] if '@' in db_url else 'Local/Unknown'}"),
            cls="container"
        )
    )

if __name__ == "__main__":
    serve()
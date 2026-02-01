from services import create_user
from models import create_question, users, questions, sessions, answers, User, Question, PracticeSession, Answer
from core import db
from datetime import datetime
from sqlalchemy import text

def init_db():
    print("Clearing database...")
    # Order matters due to Foreign Keys
    try:
        # Drop tables to handle schema changes
        db.t.answer.drop()
        db.t.practice_session.drop()
        db.t.question.drop()
        db.t.user.drop()
    except Exception as e:
        print(f"Error dropping tables: {e}")

    print("Recreating tables...")
    db.create(User)
    db.create(Question)
    db.create(PracticeSession)
    db.create(Answer)

    print("Initializing database...")

    # 1. Create Default User
    email = "me@yuan-shuai.info"
    password = "1324"
    
    print(f"Creating default user: {email}")
    create_user(email, password, role="student")

    # 2. Create Default Question
    theme = "Identity and culture"
    topic = "Sports & Leisure"
    
    print("Creating default question...")
    create_question(
        theme=theme,
        image_url="/public/img/photo1.png",
        question_1="照片里有什么？",
        question_2="你最喜欢什么运动？为什么？",
        question_3="你最近看了什么电影？",
        question_4="看电视有什么好处，有什么坏处？",
        question_5="你今天晚上想做什么？",
        question_1_en="What is there in the photo?",
        question_2_en="What sport do you like best and why?",
        question_3_en="Do you like watching films? What type of films have you seen recently?",
        topic=topic
    )

    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
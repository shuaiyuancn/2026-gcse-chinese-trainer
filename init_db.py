from services import create_user
from models import create_question, users, questions, sessions, answers
from core import db
from datetime import datetime
from sqlalchemy import text

def init_db():
    print("Clearing database...")
    # Order matters due to Foreign Keys
    try:
        with db.conn.begin():
            db.conn.execute(text("DELETE FROM answer"))
            db.conn.execute(text("DELETE FROM practice_session"))
            db.conn.execute(text("DELETE FROM question"))
            db.conn.execute(text("DELETE FROM \"user\""))
    except Exception as e:
        print(f"Error clearing tables: {e}")

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
        question_5="你今天晚上想做什么",
        topic=topic
    )

    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
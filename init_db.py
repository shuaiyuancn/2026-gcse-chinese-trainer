from services import create_user
from models import create_question, users, questions, sessions, answers, User, Question, PracticeSession, Answer
from core import db, db_url
from datetime import datetime
from sqlalchemy import text

def init_db():
    # Debug: Print DB Connection
    url = db_url
    if "@" in url:
        # Mask password: postgresql://user:pass@host... -> postgresql://user:******@host...
        try:
            part1 = url.split("@")[0]
            part2 = url.split("@")[1]
            if ":" in part1:
                scheme_user = part1.split(":")[0] + ":" + part1.split(":")[1]
                masked_url = f"{scheme_user}:******@{part2}"
            else:
                masked_url = f"{part1}:******@{part2}"
        except:
            masked_url = url # Fallback
        print(f"Connecting to Database: {masked_url}")
    else:
        print(f"Connecting to Database: {url}")

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
    try:
        create_user(email, password, role="student")
        print("Default user created successfully.")
    except Exception as e:
        print(f"Error creating default user: {e}")

    # 2. Create Default Question
    theme = "Identity and culture"
    topic = "Sports & Leisure"
    
    print("Creating default question...")
    try:
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
        print("Default question created successfully.")
    except Exception as e:
        print(f"Error creating default question: {e}")
    
    # Verify data
    try:
        q_count = questions.count
        print(f"Total questions in DB (current session): {q_count}")
        if q_count == 0:
            print("WARNING: Question table is empty. Commit might be required or insert failed.")
    except Exception as e:
        print(f"Error verifying questions: {e}")

    # Explicitly commit the changes
    print("Committing changes to database...")
    try:
        db.conn.commit()
        print("Changes committed.")
    except Exception as e:
        print(f"Error during commit: {e}")
    
    # Close connection
    try:
        db.conn.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error closing connection: {e}")

    print("Database initialization complete.")

    db.conn.commit()

if __name__ == "__main__":
    init_db()
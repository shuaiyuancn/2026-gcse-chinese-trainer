from main import create_user, create_question, users, questions, User, Question, hash_password
from datetime import datetime

def init_db():
    print("Initializing database...")

    # 1. Create Default User
    email = "me@yuan-shuai.info"
    password = "1324"
    
    # Check if user exists
    existing_users = users.rows_where("email = ?", [email])
    if not existing_users:
        print(f"Creating default user: {email}")
        create_user(email, password, role="student")
    else:
        print(f"User {email} already exists.")

    # 2. Create Default Question
    theme = "Default Photo Card"
    topic = "Sports & Leisure"
    
    # Check if question exists (by theme for simplicity)
    existing_questions = questions.rows_where("theme = ?", [theme])
    
    if not existing_questions:
        print("Creating default question...")
        create_question(
            theme=theme,
            image_url="/public/img/photo1.png",
    else:
        print("Default question already exists.")

    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()

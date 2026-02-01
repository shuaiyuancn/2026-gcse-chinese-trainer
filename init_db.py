from main import create_user, create_question, users, questions, User, Question, hash_password
from datetime import datetime

def init_db():
    print("Initializing database...")

    # 1. Create Default User
    email = "shuai"
    password = "1324"
    
    # Check if user exists
    existing_users = users.rows_where("email = ?", [email])
    if not existing_users:
        print(f"Creating default user: {email}")
        create_user(email, password, role="student")
    else:
        print(f"User {email} already exists.")

    # 2. Create Default Question
    title = "Default Photo Card"
    topic = "Sports & Leisure"
    
    # Check if question exists (by title for simplicity)
    existing_questions = questions.rows_where("title = ?", [title])
    
    if not existing_questions:
        print("Creating default question...")
        create_question(
            title=title,
            image_url="/public/img/photo1.png",
            question_1="照片里有什么？",
            question_2="你最喜欢什么运动？为什么？",
            question_3="你最近看了什么电影？",
            question_4="看电视有什么好处，有什么坏处？",
            question_5="你今天晚上想做什么",
            topic=topic
        )
    else:
        print("Default question already exists.")

    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()

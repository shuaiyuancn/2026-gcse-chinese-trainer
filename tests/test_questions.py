from main import Question, create_question, get_all_questions, get_question, update_question, delete_question

def test_question_crud():
    # 1. Create
    q_data = {
        "theme": "Sport Photo",
        "image_url": "/img/sport.jpg",
        "question_1": "Q1 Text",
        "question_2": "Q2 Text",
        "question_3": "Q3 Text",
        "question_4": "Q4 Text",
        "question_5": "Q5 Text",
        "topic": "Sports"
    }
    q = create_question(**q_data)
    assert q.id is not None
    assert q.theme == "Sport Photo"

    # 2. Read (List)
    qs = get_all_questions()
    assert len(qs) >= 1
    
    # 3. Read (Single)
    q_fetched = get_question(q.id)
    assert q_fetched.theme == "Sport Photo"

    # 4. Update
    updated_q = update_question(q.id, theme="Updated Sport Photo")
    assert updated_q.theme == "Updated Sport Photo"
    assert get_question(q.id).theme == "Updated Sport Photo"

    # 5. Delete
    delete_question(q.id)
    assert get_question(q.id) is None

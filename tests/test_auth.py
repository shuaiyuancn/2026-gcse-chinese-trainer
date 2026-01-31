from main import hash_password, verify_password, create_user, authenticate_user, User

def test_password_hashing():
    pwd = "secret"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed)
    assert not verify_password("wrong", hashed)

def test_user_creation_and_auth():
    email = "auth_test@example.com"
    pwd = "securepassword"
    
    # Create User
    user = create_user(email, pwd)
    assert user.email == email
    assert user.id is not None
    
    # Authenticate - Success
    auth_user = authenticate_user(email, pwd)
    assert auth_user is not None
    assert auth_user.email == email
    
    # Authenticate - Fail
    assert authenticate_user(email, "wrong") is None
    assert authenticate_user("nonexistent", pwd) is None


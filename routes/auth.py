from fasthtml.common import *
from services import authenticate_user, create_user, verify_password, update_password
from models import get_user_by_id

def setup_auth_routes(rt):
    @rt('/login', methods=['GET'])
    def get():
        return Titled("Login",
            Form(
                Input(name="email", type="email", placeholder="Email", required=True),
                Input(name="password", type="password", placeholder="Password", required=True),
                Button("Login"),
                action="/login", method="post"
            ),
            P(A("Sign Up", href="/signup"))
        )

    @rt('/login', methods=['POST'])
    def post(session, email: str, password: str):
        user = authenticate_user(email, password)
        if not user:
            return Titled("Login Failed", 
                P("Invalid email or password."),
                A("Try Again", href="/login")
            )
        session['user_id'] = user.id
        return Redirect('/')

    @rt('/signup', methods=['GET'])
    def get():
        return Titled("Sign Up",
            Form(
                Input(name="email", type="email", placeholder="Email", required=True),
                Input(name="password", type="password", placeholder="Password", required=True),
                Button("Sign Up"),
                action="/signup", method="post"
            ),
            P(A("Login", href="/login"))
        )

    @rt('/signup', methods=['POST'])
    def post(session, email: str, password: str):
        try:
            user = create_user(email, password)
            session['user_id'] = user.id
            return Redirect('/')
        except Exception as e:
            return Titled("Error", P(f"Could not sign up: {e}"), A("Back", href="/signup"))

    @rt('/logout', methods=['GET'])
    def get(session):
        session.clear()
        return Redirect('/')

    @rt('/profile', methods=['GET'])
    def get(session):
        user_id = session.get('user_id')
        if not user_id:
            return Redirect('/login')
        
        user = get_user_by_id(user_id)
        if not user:
             session.clear()
             return Redirect('/login')

        return Titled("Profile",
            Div(
                H5(f"Profile for {user.email}"),
                P("You can update your password below."),
                class_="section"
            ),
            Form(
                Input(name="old_password", type="password", placeholder="Current Password", required=True),
                Input(name="new_password", type="password", placeholder="New Password", required=True),
                Input(name="confirm_password", type="password", placeholder="Confirm New Password", required=True),
                Button("Update Password", cls="btn waves-effect waves-light"),
                action="/profile", method="post"
            ),
            P(A("Back to Dashboard", href="/"))
        )

    @rt('/profile', methods=['POST'])
    def post(session, old_password: str, new_password: str, confirm_password: str):
        user_id = session.get('user_id')
        if not user_id:
            return Redirect('/login')
            
        user = get_user_by_id(user_id)
        if not user:
            session.clear()
            return Redirect('/login')

        if new_password != confirm_password:
             return Titled("Error", P("New passwords do not match."), A("Try Again", href="/profile"))
        
        if not verify_password(old_password, user.password_hash):
             return Titled("Error", P("Incorrect current password."), A("Try Again", href="/profile"))

        update_password(user_id, new_password)
        
        return Titled("Success", 
            P("Password updated successfully."), 
            A("Back to Profile", href="/profile"),
            Br(),
            A("Back to Dashboard", href="/")
        )

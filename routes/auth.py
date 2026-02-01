from fasthtml.common import *
from services import authenticate_user, create_user

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

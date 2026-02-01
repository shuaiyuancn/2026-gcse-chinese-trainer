from fasthtml.common import *
from fastsql import Database
import os

# --- Database Setup ---
def get_db_url():
    # Priority 1: DATABASE_URL (set in compose.yaml or Vercel)
    url = os.getenv("DATABASE_URL")
    if url: 
        return url.replace("postgres://", "postgresql://")
    
    # Priority 2: Supabase Non-Pooling (Best for SQLAlchemy/FastSQL)
    non_pooling_url = os.getenv("POSTGRES_URL_NON_POOLING")
    if non_pooling_url: 
        return non_pooling_url.replace("postgres://", "postgresql://")

    # Priority 3: Supabase / Postgres env vars
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url: 
        return pg_url.replace("postgres://", "postgresql://")
    
    # Fallback/Default
    return "postgresql://postgres:postgres@localhost:5432/postgres"

db_url = get_db_url()
db = Database(db_url)

# --- App Setup ---
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css'),
        Link(rel='stylesheet', href='https://fonts.googleapis.com/icon?family=Material+Icons'),
        Link(rel='stylesheet', href='index.css'),
        Script(src='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'),
        Script(src='/public/recorder.js?v=2')
    ), 
    pico=False,
    secret_key=os.getenv('AUTH_SECRET', 'dev-secret')
)

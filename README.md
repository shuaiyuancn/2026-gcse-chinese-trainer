# FastHTML Hybrid Template (Windows + Podman)

A production-ready template for building "Hybrid" web applications using **FastHTML** and **FastSQL**, designed to allow dev on a **Windows Host** with a **Podman (Linux)** runtime environment.

## 🚀 Technology Stack

*   **Runtime:** Python 3.12+ (in Podman Linux Container)
*   **Web Framework:** [FastHTML](https://fastht.ml/)
*   **Database:** PostgreSQL (Production) with `psycopg2`
*   **ORM:** [FastSQL](https://github.com/AnswerDotAI/fastsql)
*   **Package Manager:** [uv](https://github.com/astral-sh/uv)
*   **Styling:** Materialize CSS (via CDN)
*   **Deployment:** Vercel (Serverless)

## 📋 Prerequisites

*   **OS:** Windows 10/11
*   **Container Runtime:** [Podman Desktop](https://podman-desktop.io/) (machine running and accessible via `podman`)
*   **Python Tooling:** [uv](https://github.com/astral-sh/uv) installed on Windows.

## 🛠️ Getting Started

Follow these steps to initialize a new project from this template:

### 1. Clone the Template Branch
Run this command to clone *only* the `template` branch into a new directory. Replace `my-new-app` with your desired project name.

```powershell
git clone -b template --single-branch https://github.com/shuaiyuancn/2026-web-app-template.git my-new-app
```

### 2. Detach from the Old Repository
Navigate into your new folder and remove the `.git` directory. This creates a "clean slate" so your new app has its own history.

```powershell
cd my-new-app
Remove-Item -Recurse -Force .git  # PowerShell command to remove the hidden .git folder
git init                          # Initialize a brand new git repository
```

### 3. Personalize the Project
Update the project identity:

1.  **`pyproject.toml`:** Change `name = "myapp"` to the project name.
2.  **`README.md`:** Update the title and description.
3.  **`compose.yaml`:** Update `container_name` for `web` and `db` services (optional but recommended).
4.  **`.env`:** Create a `.env` file if it's missing (refer to `.env.example` or just create one with `DATABASE_URL` commented out for local dev).

### 4. Launch the Environment
Initialize the workflow:

```powershell
uv sync                 # Installs dependencies on Windows (for Intellisense)
podman-compose up -d    # Builds and starts the Linux containers
```

### 5. Verify
Open `http://localhost:5001`. You should see the "Hello World" message.

**Ready to Build?**
Refer to `GEMINI.md` for the complete Agentic Development Workflow.

## 💻 Development Workflow

*   **Editing Code**: Edit files on your Windows host (`main.py`, etc.). Changes are reflected in the container (note: auto-reload depends on `uvicorn` configuration, currently set to manual restart or `uv sync` triggers).
*   **Adding Libraries**:
    1.  Run `uv add <package_name>` on Windows.
    2.  Restart the container: `podman-compose restart web`.
*   **Running Tests**:
    Tests **must** run inside the Linux container.
    ```powershell
    podman exec -it myapp_dev uv run pytest
    ```
    *(Replace `myapp_dev` with your container name if you changed it in `compose.yaml`)*

## 🌍 Deployment (Vercel)

1.  **Push** your code to a GitHub repository.
2.  **Import** the project in Vercel.
3.  **Configure Environment Variables** in Vercel Settings:
    *   `DATABASE_URL`: Connection string to your remote Postgres database (e.g., Supabase, Neon).
    *   `AUTH_SECRET`: A random string for session security.
    *   `POSTGRES_URL_NON_POOLING`: (Optional) Use if your DB provider requires a separate non-pooling URL for SQLAlchemy.
4.  **Deploy**.

Or for quick manual deployment, run
```powershell
vercel --prod
```
in the folder to initialize the config, and deploy.

## 📂 Project Structure

```
├── compose.yaml       # Podman Compose configuration
├── Dockerfile         # Python environment definition
├── GEMINI.md          # AI Agent context and instructions
├── main.py            # Application entry point
├── pyproject.toml     # Python dependencies and metadata
├── uv.lock            # Lockfile for reproducible builds
├── vercel.json        # Vercel deployment config
└── tests/             # Test suite
```

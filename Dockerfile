FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Run the application
# We use the virtual environment created by uv
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 5001
CMD ["uv", "run", "python", "main.py"]
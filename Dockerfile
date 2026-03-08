FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv --no-cache-dir

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "granian", "--interface", "asgi", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

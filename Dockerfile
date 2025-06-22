# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV POETRY_VERSION=1.8.5 \
    POETRY_CACHE_DIR=/root/.cache/pypoetry \
    PIP_CACHE_DIR=/root/.cache/pip

# System deps for building wheels and running GUI/audio
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        tk \
        libasound2 \
        git \
        && rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /app

# Install poetry
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    pip install "poetry==${POETRY_VERSION}"

# Copy only dependency files first for better cache
COPY --link pyproject.toml poetry.lock ./

# Install dependencies (main only, no dev)
RUN --mount=type=cache,target=$PIP_CACHE_DIR \
    --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --only main

# Copy the rest of the application code
COPY --link . .

# Remove unwanted files/folders (safety, but .dockerignore should handle this)
RUN rm -rf .git .gitignore .idea .ipynb_checkpoints .virtual_documents dist docs tests

FROM base AS final
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -m -g appuser appuser

# Copy installed venv and app from builder
COPY --link --from=builder /app /app

# Set permissions
RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

# Default command: open a shell, or you can set a main script if available
# If you want to run the monitor directly, you can set an entrypoint here, e.g.:
# ENTRYPOINT ["python", "-m", "is_matrix_forge.monitor"]
CMD ["bash"]

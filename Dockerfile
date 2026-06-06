# This docker file is intended to be used with docker compose to deploy a production
# instance of a Reflex app.

# Stage 1: init
FROM python:3.13 as init

ARG uv=/root/.local/bin/uv
# Clave publicable de Clerk (no secreta — va embebida en el JS del frontend)
ARG CLERK_PUBLISHABLE_KEY=""
ENV CLERK_PUBLISHABLE_KEY=${CLERK_PUBLISHABLE_KEY}

# Install `uv` for faster package bootstrapping
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Copy local context to `/app` inside container (see .dockerignore)
WORKDIR /app

# Create virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN $uv venv

# Install dependencies first (cached if requirements.txt no cambia)
COPY requirements.txt .
RUN $uv pip install -r requirements.txt

# Copy the rest of the app
COPY . .
RUN mkdir -p /app/data /app/assets/uploads /app/.states

# Deploy templates and prepare app
RUN reflex init

# Export static copy of frontend to /app/.web/build/client
RUN reflex export --frontend-only --no-zip

# Copy static files out of /app to save space in backend image
RUN mv .web/build/client /tmp/client && rm -rf .web && mkdir -p .web/build && mv /tmp/client .web/build/client

# Stage 2: copy artifacts into slim image 
FROM python:3.13-slim
WORKDIR /app
RUN adduser --disabled-password --home /app reflex
COPY --chown=reflex --from=init /app /app
RUN chown -R reflex:reflex /app/.states /app/data /app/assets/uploads
USER reflex
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1

# Needed until Reflex properly passes SIGTERM on backend.
STOPSIGNAL SIGKILL

# Always apply migrations before starting the backend.
CMD ([ -d alembic ] && reflex db migrate || true) && \
    exec reflex run --env prod --backend-only
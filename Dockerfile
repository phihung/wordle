FROM python:3.11-slim
COPY --chown=user --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN useradd -m -u 1000 user
USER user
WORKDIR /app


ADD uv.lock /app/uv.lock
ADD pyproject.toml /app/pyproject.toml

RUN uv sync --frozen --no-install-project

COPY --chown=user src ./src
RUN touch README.md

RUN uv sync --frozen
RUN . .venv/bin/activate

CMD ["uv", "run", "python", "src/wordle/ui.py"]
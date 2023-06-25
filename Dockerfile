FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV APP_DIR="/app"
ENV POETRY_VERSION=1.4.2
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1
ENV OPENAI_API_TYPE="azure"
ENV OPENAI_API_BASE="https://xebia-openai-us.openai.azure.com"
ENV OPENAI_API_VERSION="2023-03-15-preview"

WORKDIR $APP_DIR

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-dev  --no-ansi


COPY . .

RUN poetry install --only-root --no-ansi

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

ENTRYPOINT ["poetry", "run", "streamlit", "run", "src/crea_scraper/streamlit.py", "--server.port=80", "--server.address=0.0.0.0"]

#https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
FROM mcr.microsoft.com/vscode/devcontainers/python:3.9-buster

ARG YOUR_ENV=DEV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.2.1

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /crea-scraper
COPY poetry.lock pyproject.toml /crea-scraper/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == PRD && echo "--no-dev") --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /crea-scraper

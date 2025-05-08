# Use official Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

COPY wait-for-it.sh start.sh /app/
RUN chmod +x /app/start.sh /app/wait-for-it.sh

# Install Poetry
RUN pip install --upgrade pip \
 && pip install poetry

# Copy only the Poetry files (for caching)
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app

# Expose the port (FastAPI default is 8000)
EXPOSE 8002

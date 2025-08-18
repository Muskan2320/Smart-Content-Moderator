# builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml* requirements.txt* /app/
RUN pip install --upgrade pip \
 && pip wheel --wheel-dir=/wheels -r requirements.txt

# runtime
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . /app
CMD ["sh", "-c", "python manage.py migrate && gunicorn smartmod.wsgi:application -b 0.0.0.0:8000 --workers 3"]
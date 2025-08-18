FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app
CMD ["celery", "-A", "smartmod", "worker", "-l", "info"]
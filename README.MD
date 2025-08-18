# Smart Content Moderator API

## Overview
A Django-based API that analyzes user-submitted text and images for inappropriate content using Gemini LLM. 
It stores moderation results in PostgreSQL, uses Redis + Celery for async tasks, and sends Slack alerts when flagged.

## Core Stack
- Django + Django REST Framework  
- PostgreSQL (database)  
- Redis + Celery (async background tasks)  
- Google Gemini API (content classification)  
- Slack Webhooks (notifications)  
- Docker Compose (container orchestration)  

## Environment Variables
Set environment variable, look into .env.example for sample

## Setup Instructions
1. Copy `.env.example` to `.env` and fill values.  
2. Build and start containers:  
   ```bash
   docker compose up --build -d
   ```
3. Apply migrations:  
   ```bash
   docker compose exec web python manage.py migrate
   ```
4. Access API at [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

## API Endpoints
- **POST** `/api/v1/moderate/text` → `{ email, text }`  
- **POST** `/api/v1/moderate/image` → multipart `{ email, image }`  
- **GET** `/api/v1/analytics/summary?user=<email>` → analytics summary  

## Testing Examples
```bash
curl -X POST http://localhost:8000/api/v1/moderate/text   -H "Content-Type: application/json"   -d '{"email":"me@test.com","text":"I hate you"}'

curl -X POST http://localhost:8000/api/v1/moderate/image   -F email=me@test.com   -F image=@/path/to/file.jpg

curl http://localhost:8000/api/v1/analytics/summary?user=me@test.com
```

## Notifications
Slack alerts are triggered automatically when classification is **toxic**, **spam**, or **harassment**.  
Ensure `SLACK_WEBHOOK_URL` is correctly configured.

## Development Notes
- Use Django `runserver` for hot reload during development.  
- In production, web runs with Gunicorn.  
- Postgres/Redis service names in Docker Compose are `db` and `redis`.  
- Supported image types: JPEG, PNG, WEBP.  
- Classification results stored with confidence + reasoning.  

# SkillBridge — Digital Services Marketplace

> A production-grade REST API connecting businesses with digital service providers (web developers, designers, marketers).

## Live Demo
Coming soon — deploying to Fly.io

## Tech Stack
- **Backend**: FastAPI (Python 3.12) — async, type-hinted
- **Database**: PostgreSQL 16 with SQLAlchemy ORM
- **Cache**: Redis 7 — rate limiting + unread message counts
- **Queue**: Celery + Redis — background matching algorithm
- **Auth**: JWT (access + refresh token rotation), argon2 password hashing
- **CI/CD**: GitHub Actions — tests + pip-audit on every push
- **Containerization**: Docker + Docker Compose

## Architecture
Client Apps

↓

API Gateway (FastAPI + Rate Limiting + Security Headers)

↓

Core Services (Auth, Providers, Requests, Messaging, Reviews)

↓

Data Layer (PostgreSQL + Redis)

↑

Background Workers (Celery — matching algorithm, notifications)

## Key Features
- Role-based auth — client, provider, admin with JWT refresh token rotation
- Provider matching algorithm — scores providers by rating and category
- Real-time messaging — WebSocket with Redis-backed unread counts
- Admin moderation — provider approval queue, audit logging
- Rate limiting — Redis sliding window on all public endpoints
- Security headers — CSP, X-Frame-Options, Permissions-Policy

## Security Considerations

| Threat | Mitigation |
|--------|-----------|
| Credential stuffing | argon2 hashing + rate limiting 5 req/min on /register |
| IDOR attacks | Ownership checks on every data-fetch endpoint |
| SQL injection | SQLAlchemy ORM parameterised queries |
| XSS | Content-Security-Policy header |
| Token theft | Short-lived JWT 15min + refresh token rotation |
| Dependency vulnerabilities | pip-audit in CI pipeline |

## Performance Metrics
Tested with 50 concurrent users on local machine (Docker):

| Endpoint | Median | p95 | p99 |
|----------|--------|-----|-----|
| GET /providers | 24ms | 75ms | 277ms |
| GET /health | 3ms | 13ms | 150ms |
| GET /requests | 7ms | 20ms | 46ms |

- Sustained RPS: 23 requests/second
- Failure rate: less than 1 percent
- Test coverage: 66 percent (11 automated tests)

## Setup

```bash
git clone https://github.com/yourusername/skillbridge
cd skillbridge
cp .env.example .env
docker-compose up --build
```

API docs: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register client or provider |
| POST | /auth/login | Login, get JWT token |
| GET | /auth/me | Get current user |
| POST | /providers/profile | Create/update provider profile |
| GET | /providers | Search providers |
| PATCH | /providers/:id/approve | Admin approve provider |
| POST | /requests | Post service request |
| POST | /requests/:id/proposals | Submit proposal |
| PATCH | /requests/proposals/:id/accept | Accept proposal |
| POST | /messages/conversations | Start conversation |
| POST | /messages/conversations/:id | Send message |
| POST | /reviews | Submit review |

## Project Structure
app/

├── models/      — SQLAlchemy DB models

├── routers/     — FastAPI route handlers

├── schemas/     — Pydantic request/response schemas

├── services/    — Business logic

└── utils/       — Auth, rate limiting, security

## Running Tests

```bash
docker-compose exec -e ENV=test api pytest tests/ -v --cov=app
```
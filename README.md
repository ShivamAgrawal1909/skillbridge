# SkillBridge — Digital Services Marketplace API

A production-ready **digital services marketplace** built with **FastAPI**, **PostgreSQL**, **Redis**, and **Docker**. It connects small businesses with verified digital service providers through a secure request–proposal–hire workflow, while providing real-time messaging, provider verification, background job processing, and an administrative moderation system.

---

# Tech Stack

| Layer             | Technology                    |
| ----------------- | ----------------------------- |
| Framework         | FastAPI (Python 3.12)         |
| ORM               | SQLAlchemy 2.x (Async ORM)    |
| Database          | PostgreSQL 16                 |
| Cache             | Redis 7                       |
| Background Tasks  | Celery + Redis                |
| Authentication    | JWT (Access + Refresh Tokens) |
| Password Security | argon2id                      |
| Validation        | Pydantic v2                   |
| Monitoring        | Prometheus + Grafana          |
| Testing           | Pytest                        |
| CI/CD             | GitHub Actions + pip-audit    |
| Containers        | Docker & Docker Compose       |
| Deployment        | Render                        |

---

# Architecture

```
Client Applications
        │
        ▼
FastAPI Application
(Security Middleware, Rate Limiting, Authentication)
        │
        ▼
Business Services
├── Authentication
├── Provider Management
├── Service Requests
├── Proposal Management
├── Messaging
├── Reviews
└── Admin Operations
        │
        ▼
Persistence Layer
├── PostgreSQL
└── Redis
        ▲
        │
Background Workers
(Celery + Redis)
```

---

# Project Structure (High Level)

```
skillbridge/
├── app/
│   ├── models/             # SQLAlchemy models
│   ├── routers/            # API endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── utils/              # Authentication, rate limiting, helpers
│   ├── middleware/         # Security middleware
│   ├── core/               # Config and settings
│   └── main.py             # FastAPI application
│
├── alembic/                # Database migrations
├── tests/                  # Pytest suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# Platform Overview

SkillBridge enables businesses to discover trusted digital professionals through a structured marketplace.

Clients can create service requests, receive proposals from verified providers, compare offers, hire providers, exchange messages, and leave reviews after project completion.

Providers maintain public profiles, browse matching opportunities, submit proposals, communicate with clients, and build reputation through ratings.

Administrators oversee platform integrity by approving providers, moderating reviews, resolving disputes, and monitoring system activity.

---

# Authentication & Security

The platform implements multiple security layers suitable for production environments.

### Authentication

* JWT Access Tokens (15 minutes)
* Refresh Token Rotation (7 days)
* Refresh tokens stored hashed in PostgreSQL
* Stateless authentication
* Role-based authorization

### Password Security

* argon2id hashing
* Password hashes never exposed
* Secure verification process

### Authorization Roles

* Client
* Provider
* Administrator

### Security Features

* Redis Sliding Window Rate Limiting
* Security Headers
* Content Security Policy
* Referrer Policy
* X-Frame-Options
* X-XSS-Protection
* Audit Logging
* Ownership validation on protected resources

---

# Client Features

Authenticated clients can:

* Register and login securely
* Manage personal account
* Create service requests
* Browse verified providers
* View provider profiles
* Receive provider proposals
* Accept provider proposals
* Start conversations
* Exchange real-time messages
* Submit provider reviews
* View request history

---

# Provider Features

Verified providers can:

* Create professional profile
* Update skills and categories
* Browse open client requests
* Submit proposals
* Manage active conversations
* Receive request notifications
* Track reviews and ratings
* Build public reputation

Providers remain **Pending** until approved by an administrator.

---

# Admin Features

Administrator dashboard includes moderation and platform management tools.

### Provider Management

* Review provider applications
* Approve providers
* Suspend providers
* Reactivate providers
* View provider activity

### User Management

* View registered users
* Moderate accounts
* Review audit logs

### Reviews

* Monitor submitted reviews
* Remove inappropriate content

### Platform Operations

* Resolve disputes
* Monitor activity
* Review authentication events

---

# Provider Matching

Whenever a client submits a service request, a Celery background task evaluates approved providers.

Current scoring weights:

| Factor          | Weight |
| --------------- | ------ |
| Category Match  | 50%    |
| Provider Rating | 30%    |
| Response Time   | 20%    |

Top matching providers are selected for notification.

The matching process executes asynchronously and does not delay API responses.

---

# Messaging System

SkillBridge includes a built-in messaging service.

Features include:

* Real-time WebSocket messaging
* Conversation management
* Redis unread message counters
* REST fallback polling
* Authenticated conversations only

---

# Performance

Application performance was tested using **Locust** with **50 concurrent users** running inside Docker.

| Endpoint       | Median | p95   | p99    |
| -------------- | ------ | ----- | ------ |
| GET /health    | 3 ms   | 13 ms | 150 ms |
| GET /providers | 24 ms  | 75 ms | 277 ms |
| GET /requests  | 7 ms   | 20 ms | 46 ms  |

Additional observations:

* Sustained approximately **23 requests/second**
* Failure rate below **1%**
* Redis reduced repeated database lookups for frequently accessed counters
* Background jobs prevented long-running request blocking

---

# Monitoring

Application metrics are exposed for Prometheus.

Grafana dashboards monitor:

* Total Requests
* Request Rate
* Active Connections
* Response Time
* p95 Latency
* p99 Latency
* Error Rate

---

# Security Considerations

| Threat                     | Mitigation                             |
| -------------------------- | -------------------------------------- |
| Credential Stuffing        | argon2id hashing + Redis rate limiting |
| SQL Injection              | SQLAlchemy parameterized queries       |
| IDOR                       | Ownership validation                   |
| Cross Site Scripting       | Content Security Policy                |
| Token Theft                | Short-lived JWT + Refresh Rotation     |
| Brute Force                | Login rate limiting                    |
| Sensitive Data Exposure    | Password hashes never returned         |
| Dependency Vulnerabilities | pip-audit executed in CI               |

---

# API Endpoints

## Authentication

| Method | Endpoint       | Description                 |
| ------ | -------------- | --------------------------- |
| POST   | /auth/register | Register client or provider |
| POST   | /auth/login    | Login                       |
| POST   | /auth/refresh  | Refresh access token        |
| GET    | /auth/me       | Current authenticated user  |

---

## Providers

| Method | Endpoint                | Description              |
| ------ | ----------------------- | ------------------------ |
| POST   | /providers/profile      | Create or update profile |
| GET    | /providers              | Search providers         |
| GET    | /providers/{id}         | Provider profile         |
| PATCH  | /providers/{id}/approve | Admin approval           |
| PATCH  | /providers/{id}/suspend | Suspend provider         |

---

## Requests

| Method | Endpoint                        | Description     |
| ------ | ------------------------------- | --------------- |
| POST   | /requests                       | Create request  |
| GET    | /requests                       | Client requests |
| GET    | /requests/open                  | Open requests   |
| POST   | /requests/{id}/proposals        | Submit proposal |
| GET    | /requests/{id}/proposals        | View proposals  |
| PATCH  | /requests/proposals/{id}/accept | Accept proposal |

---

## Messaging

| Method | Endpoint                     | Description         |
| ------ | ---------------------------- | ------------------- |
| GET    | /messages/conversations      | List conversations  |
| POST   | /messages/conversations      | Create conversation |
| POST   | /messages/conversations/{id} | Send message        |

---

## Reviews

| Method | Endpoint               | Description      |
| ------ | ---------------------- | ---------------- |
| POST   | /reviews               | Submit review    |
| GET    | /reviews/provider/{id} | Provider reviews |

---

# Environment Variables

Example `.env`

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/skillbridge
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ENV=development
```

---

# Running Locally

Clone the repository:

```bash
git clone https://github.com/ShivamAgrawal1909/skillbridge
cd skillbridge
```

Create an environment file:

```bash
cp .env.example .env
```

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the application:

```bash
docker-compose up --build
```

API Documentation:

```
http://localhost:8000/docs
```

---

# Running Tests

```bash
docker-compose exec -e ENV=test api pytest tests/ -v --cov=app
```

Current test suite:

* 28 automated tests
* 69% code coverage

---

# Deployment

The application is containerized using Docker and deployed on Render.

Production stack includes:

* FastAPI API Service
* PostgreSQL
* Redis
* Celery Workers
* Prometheus Metrics
* Grafana Dashboard

---

# Planned Integrations

The following integrations have already been designed but require production credentials.

| Integration                              | Status                      |
| ---------------------------------------- | --------------------------- |
| WhatsApp Business Notifications          | Pending API credentials     |
| Email Verification (SendGrid)            | Pending API key             |
| File Uploads (Amazon S3 / Cloudflare R2) | Storage credentials pending |
| Sentry Error Monitoring                  | DSN configuration pending   |

---

# License

This project is intended for educational, learning, and portfolio purposes.

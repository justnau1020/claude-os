---
tags: [project, example, architecture]
keywords: example project, REST API, authentication, deployment
aliases: [the project, main app]
priority: high
---

# Example Project

## Architecture
FastAPI backend with PostgreSQL. Deployed on AWS ECS behind ALB.

## Auth
JWT tokens with refresh rotation. API keys for service-to-service.

## Key Directories
- `src/api/` — Route handlers
- `src/core/` — Business logic
- `src/db/` — Models and migrations
- `tests/` — Pytest suite

## Deployment
- Staging: auto-deploy on merge to `develop`
- Production: manual deploy via `/deploy` skill after PR review

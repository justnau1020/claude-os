---
name: api-conventions
description: API development conventions and patterns. Applies when writing or modifying API routes, MCP tools, or CLI commands -- covers authentication, ownership enforcement, error responses, and route organization.
user-invocable: false
---

# API Development Conventions

These conventions apply when working on the API layer (routes, MCP tools, CLI commands).

## Authentication
- All endpoints require valid authentication (Bearer token, session cookie, or API key)
- Use dependency injection for auth (e.g., `Depends(get_current_user)` in FastAPI)
- Provide both required and optional auth dependencies where appropriate
- Rate limit registration and auth endpoints to prevent brute-force
- Resource ownership is enforced -- users can only access their own resources

## Route Organization
- One route file per resource domain: `routes_users.py`, `routes_orders.py`, etc.
- Each route file defines a router (e.g., `APIRouter` in FastAPI)
- Routers are registered in the main app file

## Error Responses
- `422` -- Validation errors (malformed input)
- `404` -- Resource not found
- `429` -- Rate limits (pass through from upstream with reset timing)
- `503` -- Upstream service unavailability
- Error messages must be specific and actionable, not generic

## Resource Ownership
- Every endpoint that accesses a user's resource must verify ownership
- Use the dependency injection pattern for ownership checks
- Never allow cross-user resource access

## MCP Server (if applicable)
- Tools mirror REST API functionality
- Each tool has a clear description to help LLMs understand when to use it
- Include example parameter values in descriptions
- Return strings for LLM consumption

## CLI (if applicable)
- Commands organized by resource domain
- Consistent flag naming across commands
- Help text on every command and argument

## Middleware
- Security middleware for headers, CORS, CSP
- Rate limiting middleware
- All middleware must be async (if using async framework)

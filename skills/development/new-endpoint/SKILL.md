---
name: new-endpoint
description: Scaffold a new REST API endpoint. Use when adding a new API route or extending the REST API with new functionality.
disable-model-invocation: true
argument-hint: <method> <path> [description]
---

# Create a New API Endpoint

Scaffold a new REST API endpoint following the project's existing conventions.

## Arguments

- `$0` -- HTTP method (GET, POST, PUT, DELETE)
- `$1` -- Route path (e.g., `/users/{user_id}/settings`)
- `$2` -- Optional description of what the endpoint does

## Steps

### 1. Determine route file

Check if an existing route file covers this domain (read the API directory for existing route files). If this fits an existing domain, add to that file. Otherwise, create a new route file.

### 2. Create the endpoint

Follow patterns from existing routes in the project. Example (FastAPI):

```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/resource", tags=["domain"])

@router.$0("$1")
async def endpoint_name(
    resource_id: str,
    user=Depends(get_current_user),
):
    ...
```

### 3. Conventions (NON-NEGOTIABLE)

- **Authentication**: Use the project's auth dependency injection pattern
- **Typed models**: Request/response bodies use typed models, not raw dicts
- **Error responses**: Use specific HTTP status codes (422, 404, 429, 503) with actionable messages
- **Async only**: All endpoint functions must be `async def`
- **Type hints**: Full type annotations on all parameters and return types

### 4. Register the router

If you created a new route file, register it in the app's router registration (e.g., `app.include_router()`).

### 5. Write tests

Create or extend tests for the new endpoint:
- Test successful request with valid auth
- Test unauthorized access (missing/invalid credentials)
- Test ownership enforcement (if applicable)
- Test validation errors (bad input)
- Test edge cases specific to this endpoint

### 6. Verify

```bash
pytest tests/ -v -k "test_<domain>"
```

---
name: dashboard-conventions
description: Dashboard/frontend development conventions -- vanilla HTML/JS/CSS patterns, theming, and API integration. Applies when modifying frontend files.
user-invocable: false
---

# Dashboard Conventions

These conventions apply when working on the frontend/dashboard.

## Architecture
- **No build step preferred**: Vanilla HTML/JS/CSS served directly (if applicable)
- **Minimal dependencies**: Prefer CDN-hosted libraries over npm packages where possible
- **Theme system**: CSS custom properties for all colors, enabling dark/light theme support

## Patterns
- **API calls**: Use `fetch()` with proper error handling and auth headers
- **Polling**: Configurable interval for real-time data updates (if not using WebSocket/SSE)
- **Responsive**: Desktop-primary with responsive breakpoints for mobile
- **CSS variables**: All theme colors defined as custom properties

## File organization
- One HTML file per page/view
- Matching JS file for logic (e.g., `dashboard.html` + `dashboard.js`)
- Shared styles in a common stylesheet, page-specific styles in dedicated files
- Assets organized in dedicated directories (images, icons, fonts)

## API Integration
- All API calls go through a shared fetch wrapper that handles auth and errors
- Loading states shown during API calls
- Error states display actionable messages to users
- Optimistic updates where appropriate, with rollback on failure

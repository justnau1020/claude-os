---
name: new-mcp-tool
description: Add a new MCP tool to a FastMCP server. Use when adding a new tool for LLM agents or extending the MCP interface with new functionality.
disable-model-invocation: true
argument-hint: <tool-name>
---

# Add a New MCP Tool

Add a tool to the project's FastMCP server.

## Arguments

- `$ARGUMENTS` -- Tool name in snake_case (e.g., `get_user_profile`)

## Steps

### 1. Read the existing MCP server

Read the MCP server file to understand current tool patterns and the FastMCP setup.

### 2. Add the tool

```python
@mcp.tool()
async def $ARGUMENTS(
    param1: str,
    param2: int = 10,
) -> str:
    """Clear description of what this tool does and when an LLM should use it.

    Include example parameter values to help LLMs understand expected input.
    Example: param1="example_value", param2=30
    """
    ...
```

### 3. Tool description conventions

The tool description is critical -- it's how LLMs decide when to call it:
- First sentence: what the tool does
- Second sentence: when to use it
- Include parameter examples inline
- Mention any constraints (rate limits, data availability)

### 4. Implementation conventions

- **Async only**: All tool functions must be `async def`
- **Return strings**: MCP tools return string responses for LLM consumption
- **Actionable errors**: If something fails, return a helpful error string, not a generic one
- **Respect data boundaries**: All data queries should respect the project's access control and data validation rules

### 5. Write tests

Add tests for the new tool's logic. Test:
- Happy path with valid parameters
- Error handling with invalid parameters
- Data validation on returned data

### 6. Verify

```bash
pytest tests/ -v -k "mcp"
```

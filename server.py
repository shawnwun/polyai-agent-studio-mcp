#!/usr/bin/env python3
"""
PolyAI Agent Studio MCP Server

Exposes the Cursor rules from the agent-deployments repo as MCP tools and resources.
"""

import os
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

RULES_DIR = Path(__file__).parent / "rules"

mcp = FastMCP(
    name="polyai-agent-studio",
    instructions=(
        "This server provides the official PolyAI Agent Studio development rules. "
        "Use list_rules to discover what rules are available, get_rule to fetch a specific rule, "
        "and search_rules to find rules relevant to a topic."
    ),
)


def _load_rule(path: Path) -> dict:
    """Parse a .mdc file, extracting frontmatter and body."""
    text = path.read_text(encoding="utf-8")
    name = path.stem  # e.g. "agent-studio-flows"

    # Parse YAML frontmatter (--- ... ---)
    description = ""
    tags: list[str] = []
    body = text
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            frontmatter = text[3:end].strip()
            body = text[end + 3 :].strip()
            for line in frontmatter.splitlines():
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')
                elif line.startswith("tags:"):
                    tags_str = line.split(":", 1)[1].strip()
                    tags = [t.strip().strip('"').strip("'") for t in re.findall(r"[\w-]+", tags_str)]

    return {
        "name": name,
        "description": description,
        "tags": tags,
        "content": body,
        "filename": path.name,
    }


def _all_rules() -> list[dict]:
    rules = []
    for path in sorted(RULES_DIR.glob("*.mdc")):
        rules.append(_load_rule(path))
    return rules


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def list_rules() -> str:
    """
    List all available PolyAI Agent Studio rules.
    Returns a summary of each rule with its name, description, and tags.
    """
    rules = _all_rules()
    lines = [f"# PolyAI Agent Studio Rules ({len(rules)} total)\n"]
    for r in rules:
        tags_str = ", ".join(r["tags"]) if r["tags"] else "—"
        lines.append(f"## `{r['name']}`")
        lines.append(f"**Description:** {r['description']}")
        lines.append(f"**Tags:** {tags_str}\n")
    return "\n".join(lines)


@mcp.tool()
def get_rule(name: str) -> str:
    """
    Get the full content of a specific Agent Studio rule.

    Args:
        name: Rule name (without .mdc extension), e.g. "agent-studio-flows"
              or "agent-studio-topics". Use list_rules to see all available names.
    """
    # Normalise: allow passing with or without extension
    name = name.removesuffix(".mdc")

    path = RULES_DIR / f"{name}.mdc"
    if not path.exists():
        # Try fuzzy match
        candidates = [p.stem for p in RULES_DIR.glob("*.mdc")]
        close = [c for c in candidates if name.lower() in c.lower()]
        if len(close) == 1:
            path = RULES_DIR / f"{close[0]}.mdc"
        elif close:
            return (
                f"Rule '{name}' not found. Did you mean one of: "
                + ", ".join(f"`{c}`" for c in close)
                + "?\nUse list_rules() to see all available rules."
            )
        else:
            return (
                f"Rule '{name}' not found. "
                "Use list_rules() to see all available rules."
            )

    rule = _load_rule(path)
    header = f"# Rule: `{rule['name']}`\n**{rule['description']}**\n\n---\n\n"
    return header + rule["content"]


@mcp.tool()
def search_rules(query: str) -> str:
    """
    Search across all Agent Studio rules for content matching a query.

    Args:
        query: Search term or phrase to look for (case-insensitive).
    """
    query_lower = query.lower()
    results = []

    for rule in _all_rules():
        content_lower = rule["content"].lower()
        name_lower = rule["name"].lower()
        desc_lower = rule["description"].lower()

        # Count hits
        hits = content_lower.count(query_lower)
        in_name = query_lower in name_lower
        in_desc = query_lower in desc_lower

        if hits > 0 or in_name or in_desc:
            # Extract up to 3 context snippets
            snippets = []
            start = 0
            for _ in range(3):
                idx = content_lower.find(query_lower, start)
                if idx == -1:
                    break
                snippet_start = max(0, idx - 80)
                snippet_end = min(len(rule["content"]), idx + len(query) + 80)
                snippet = rule["content"][snippet_start:snippet_end].strip()
                snippets.append(f"  …{snippet}…")
                start = idx + 1

            results.append(
                {
                    "name": rule["name"],
                    "description": rule["description"],
                    "hits": hits,
                    "snippets": snippets,
                }
            )

    if not results:
        return f"No rules found containing '{query}'."

    results.sort(key=lambda r: r["hits"], reverse=True)
    lines = [f"# Search results for '{query}' ({len(results)} rules)\n"]
    for r in results:
        lines.append(f"## `{r['name']}` — {r['hits']} match(es)")
        lines.append(f"_{r['description']}_")
        for s in r["snippets"]:
            lines.append(s)
        lines.append("")
    return "\n".join(lines)


@mcp.tool()
def get_all_rules() -> str:
    """
    Get the full content of ALL Agent Studio rules concatenated.
    Use this when you need a complete picture of all guidelines at once.
    """
    rules = _all_rules()
    sections = []
    for r in rules:
        sections.append(f"{'=' * 60}")
        sections.append(f"RULE: {r['name']}")
        sections.append(f"{'=' * 60}")
        sections.append(r["content"])
        sections.append("")
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Resources — each rule is also accessible as a resource URI
# ---------------------------------------------------------------------------


@mcp.resource("polyai://rules/{name}")
def rule_resource(name: str) -> str:
    """Access an Agent Studio rule as a resource."""
    return get_rule(name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    port = int(os.environ.get("PORT", 8000))
    transport = os.environ.get("MCP_TRANSPORT", "sse")

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # SSE transport with an extra /health endpoint for Railway
        async def health(request: Request) -> JSONResponse:
            rules = _all_rules()
            return JSONResponse(
                {"status": "ok", "rules_loaded": len(rules), "server": "polyai-agent-studio-mcp"}
            )

        # Build the SSE app from fastmcp and add our health route
        sse_app = mcp.sse_app()
        app = Starlette(
            routes=[
                Route("/health", health),
                Mount("/", app=sse_app),
            ]
        )
        uvicorn.run(app, host="0.0.0.0", port=port)

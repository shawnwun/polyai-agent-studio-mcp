# PolyAI Agent Studio MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes the PolyAI Agent Studio Cursor rules as tools and resources, making them available to any MCP-compatible client (Claude Desktop, Cursor, etc.).

## Tools

| Tool | Description |
|------|-------------|
| `list_rules` | List all 13 available rules with descriptions and tags |
| `get_rule(name)` | Get the full content of a specific rule |
| `search_rules(query)` | Search across all rules for a keyword |
| `get_all_rules` | Get all rules concatenated (full context dump) |

## Available Rules

- `agent-studio-anti-patterns` — Common mistakes and anti-patterns to avoid
- `agent-studio-conversation-style` — Natural language and conversation style guidelines
- `agent-studio-entities` — Entity definition patterns
- `agent-studio-flows` — Flow structure, step prompts, navigation
- `agent-studio-lifecycle-functions` — start/end function patterns
- `agent-studio-low-code-flows` — Low-code flow configuration
- `agent-studio-project-structure` — Project directory layout and required files
- `agent-studio-state-and-metrics` — State management and metrics tracking
- `agent-studio-topics` — Topic YAML format and patterns
- `agent-studio-utterances` — Utterance/example query guidelines
- `agent-studio-writing-functions` — Python function writing patterns
- `call-diagnostics` — Call diagnostics patterns
- `call-diagnostics-trigger` — Call diagnostics trigger configuration

## Running Locally

```bash
# stdio (for Claude Desktop / Cursor)
python server.py

# SSE HTTP server
MCP_TRANSPORT=sse PORT=8000 python server.py
```

### Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "polyai-agent-studio": {
      "command": "python",
      "args": ["/path/to/polyai-agent-studio-mcp/server.py"],
      "env": { "MCP_TRANSPORT": "stdio" }
    }
  }
}
```

### Remote (hosted) config

```json
{
  "mcpServers": {
    "polyai-agent-studio": {
      "url": "https://YOUR-RAILWAY-URL/mcp"
    }
  }
}
```

## Deploying to Railway

1. Fork / push this repo to GitHub
2. Go to [railway.app](https://railway.app), create a new project → Deploy from GitHub repo
3. Railway auto-detects the Dockerfile and deploys
4. Set env vars if needed (defaults work out of the box)
5. Your MCP server will be available at `https://<your-app>.up.railway.app/sse`

## Health Check

```
GET /health
```
Returns:
```json
{"status": "ok", "rules_loaded": 13, "server": "polyai-agent-studio-mcp"}
```

## Updating Rules

Rules are stored in `rules/*.md`. To update:
1. Copy new/updated `.md` files into `rules/`
2. Push to GitHub — Railway redeploys automatically

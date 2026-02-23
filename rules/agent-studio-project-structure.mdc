---
description: Agent Studio project directory structure and required files
tags: [agent-studio, structure, project, local-development]
---

# Agent Studio Project Structure

## Common Patterns

Each Agent Studio project typically has:

- `imports.py` - Auto-generated, imports from poly_core
- `gen_decorators.py` - Local decorator definitions
- `functions/` - Global function definitions
- `flows/` - Flow definitions (each flow has its own folder with functions and steps)
- `topics/` - Topic definitions (optional)
- `agent_settings/` - Agent configuration

## Standard Project Structure

```
project/
├── gen_decorators.py        # Auto-generated decorators
├── imports.py               # Auto-generated imports
├── functions/               # Global function definitions
│   ├── global_func_1.py
│   ├── global_func_2.py
│   └── ...
├── flows/                   # Flow definitions
│   ├── flow_name_1/        # Flow folder (named after flow)
│   │   ├── flow_name_1.yaml    # Flow definition YAML
│   │   ├── flow_config.yaml    # Flow configuration
│   │   ├── functions/          # Flow-specific functions
│   │   │   ├── flow_func_1.py
│   │   │   └── flow_func_2.py
│   │   └── steps/              # Flow step definitions
│   │       ├── step_1.yaml
│   │       └── step_2.yaml
│   ├── flow_name_2/
│   │   ├── flow_name_2.yaml
│   │   ├── flow_config.yaml
│   │   ├── functions/
│   │   └── steps/
│   └── ...
└── topics/                  # Knowledge base YAML files
    ├── topic-1.yaml
    ├── topic-2.yaml
    └── ...
```

## Flow Structure Details

Each flow folder contains:

- **Flow YAML file** (`<flow_name>.yaml`) - Main flow definition
- **`flow_config.yaml`** - Flow-specific configuration
- **`functions/`** - Python functions specific to this flow
- **`steps/`** - YAML files defining each step in the flow

Flow-specific functions are organized within their respective flow folders, not in the global `functions/` directory. Global functions that are shared across multiple flows remain in the root `functions/` directory.

## Import Pattern

All function files use:

```python
from imports import *  # <AUTO GENERATED>
```

This imports:

- `Conversation` from `poly_platform.function_runtime.conversation`
- `func_description`, `func_parameter` from local `gen_decorators`
- Various other poly_core utilities

**NEVER** manually edit `imports.py` - it's auto-generated.

## Files to NOT Commit to Git

Add to `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

The config files (ruff.toml, pyrightconfig.json, etc.) SHOULD be committed so the setup is shared across team members.

---
name: openclaw-cli
version: 0.1.0
summary: "Read-only OpenClaw CLI health and status tools — runs inside openclaw container"
description: >
  Provides a safe, read-focused interface to the `openclaw` CLI for health,
  models, channels, gateway status, and memory search.
  This skill runs natively inside the openclaw_gateway container where the
  `openclaw` binary is available.

  Mutating commands (restart, config set, cron add, channel add/remove, gateway
  uninstall/reset) are out of scope and require 888_HOLD + human approval.

floors:
  - F1   # read-only; no state mutation
  - F2   # return only what the CLI actually reports
  - F4   # structured output, no noise
  - F7   # mark failures/unknowns explicitly
  - F9   # not a being; this is a diagnostic tool
  - F11  # operator-only; no unauthenticated execution
  - F12  # no shell injection; args are hardcoded, not user-supplied
  - F13  # Arif retains veto on any mutating action

safety:
  irreversible: false
  calls_shell: true
  shell_scope: "openclaw * --json only (read-only subcommands)"
  notes: >
    All commands use the --json flag where available.
    No restart, uninstall, reset, config set, or channel mutation commands
    are implemented in this skill.

tools:
  - id: openclaw_get_health
    description: "Gateway liveness — openclaw health --json"
    input:
      type: object
      properties: {}
      required: []

  - id: openclaw_get_status
    description: "Full status overview — openclaw status --json --all"
    input:
      type: object
      properties: {}
      required: []

  - id: openclaw_list_models
    description: "List configured models — openclaw models list --json"
    input:
      type: object
      properties:
        provider:
          type: string
          description: "Optional provider filter (e.g. 'moonshot', 'anthropic')."
      required: []

  - id: openclaw_get_models_status
    description: "Model auth and quota status — openclaw models status --json"
    input:
      type: object
      properties: {}
      required: []

  - id: openclaw_channels_status
    description: "Channel health — openclaw channels status --probe --json"
    input:
      type: object
      properties:
        channel:
          type: string
          description: "Optional: whatsapp, telegram, discord, slack, etc."
      required: []

  - id: openclaw_memory_search
    description: "Semantic search over memory files — openclaw memory search"
    input:
      type: object
      properties:
        query:
          type: string
          description: "Free-text search query."
      required: ["query"]

  - id: openclaw_gateway_status
    description: "Gateway service status — openclaw gateway status --json"
    input:
      type: object
      properties: {}
      required: []
---

# openclaw-cli Skill

Read-only OpenClaw CLI diagnostics. This skill runs **inside the `openclaw_gateway`
container** where the `openclaw` binary is available at `/usr/local/bin/openclaw`
(or via the `node_modules/.bin/openclaw` path).

## Environment note

On the arifOS VPS, `openclaw` is NOT available on the host PATH — it lives inside
the container. This skill must be loaded and executed by the OpenClaw agent itself
(which runs inside the container). It is NOT a Python MCP tool.

For MCP-layer access, see `aaa_mcp/integrations/openclaw_gateway_client.py` which
provides the HTTP-observable subset (health probe + config snapshot) via the
`query_openclaw` MCP tool.

## 888_HOLD boundary

The following are explicitly OUT OF SCOPE for this skill:
- `openclaw gateway restart / stop / uninstall`
- `openclaw config set`
- `openclaw cron add / edit / rm`
- `openclaw channels add / remove`
- `openclaw reset / uninstall`

Any of the above require 888_HOLD and explicit human confirmation from Arif.

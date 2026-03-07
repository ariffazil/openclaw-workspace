---
name: openclaw-sessions
description: Manage OpenClaw sessions, sub-agents, and multi-agent orchestration. Use when: (1) listing active sessions or sub-agents, (2) spawning background sub-agent tasks, (3) sending messages to other sessions, (4) checking session history or status, (5) killing stuck sub-agents, (6) steering running sub-agents, (7) user asks about "sessions", "sub-agents", "background tasks", "spawn agent", "parallel work", or "what's running".
---

# OpenClaw Sessions & Sub-Agents Skill

## List Sessions

View active sessions:
- `sessions_list()` — all sessions
- `sessions_list(activeMinutes=60)` — active in last hour
- `sessions_list(kinds=["subagent"], messageLimit=1)` — sub-agents only

## Session History

Read another session's messages:
- `sessions_history(sessionKey="<key>", limit=20)`
- `sessions_history(sessionKey="<key>", includeTools=true)` — include tool calls

## Send to Another Session

Inject a message into another session:
- `sessions_send(sessionKey="<key>", message="Check this out")`
- `sessions_send(label="<label>", message="Update needed")` — by label

## Spawn Sub-Agent (Background Work)

For parallel/background tasks:

```
sessions_spawn(
  task="Research the latest OpenClaw release notes and summarize",
  mode="run"           # one-shot (completes and announces)
)
```

Options:
- `mode="run"` — one-shot, announces result when done
- `mode="session"` — persistent, stays alive for follow-ups
- `model="anthropic/claude-sonnet-4-6"` — use a different model
- `thinking="high"` — enable deep thinking
- `label="research"` — friendly name
- `runTimeoutSeconds=300` — 5 min timeout
- `cleanup="delete"` — auto-cleanup when done

### ACP Harness (Codex, Claude Code)

For coding agents in threads:
```
sessions_spawn(
  runtime="acp",
  agentId="<agent-id>",
  task="Fix the bug in server.py",
  thread=true,
  mode="session"
)
```

## Manage Sub-Agents

List running sub-agents:
- `subagents(action="list")`
- `subagents(action="list", recentMinutes=30)` — last 30 min

Steer a running sub-agent:
- `subagents(action="steer", target="<id>", message="Focus on the API layer")`

Kill a stuck sub-agent:
- `subagents(action="kill", target="<id>")`
- `subagents(action="kill", target="all")` — kill all

## Session Status

Check current session details:
- `session_status()` — usage, model, time, cost

Override model for this session:
- `session_status(model="anthropic/claude-opus-4-6")` — switch model
- `session_status(model="default")` — reset to default

## When to Use Sub-Agents

| Scenario | Approach |
|---|---|
| Quick answer | Direct reply (no sub-agent) |
| Long research task | `sessions_spawn(mode="run")` |
| Parallel work items | Multiple spawns with labels |
| Coding task in thread | `sessions_spawn(runtime="acp", thread=true)` |
| Monitor background | `subagents(action="list")` |

## Sub-Agent Config

Default model for sub-agents (in openclaw.json):
```json5
"agents": {
  "defaults": {
    "subagents": {
      "model": "kimi/kimi-k2.5",
      "maxConcurrent": 1,
      "runTimeoutSeconds": 900
    }
  }
}
```

## Constraints

- Sub-agents run in isolated sessions (no main context)
- Each sub-agent has its own token usage
- `maxConcurrent` limits parallel runs (default: 1)
- Sub-agents auto-announce results to requester chat
- Don't poll subagents in a loop — completion is push-based

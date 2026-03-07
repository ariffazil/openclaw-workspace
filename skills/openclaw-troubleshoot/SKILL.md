---
name: openclaw-troubleshoot
description: Diagnose and fix OpenClaw gateway issues, model failures, channel problems, and service degradation. Use when: (1) gateway is unresponsive or slow, (2) messages aren't being delivered, (3) models are failing or timing out, (4) cron jobs aren't firing, (5) memory search returns empty, (6) bot appears offline, (7) user reports "broken", "not working", "error", "stuck", "offline", "fix", or "debug".
---

# OpenClaw Troubleshoot Skill

Systematic diagnostics for when things break.

## Step 1: Quick Health Check

Run these in order (fast to slow):

```bash
# 1. Gateway alive?
openclaw status

# 2. Logs from last 5 minutes
tail -50 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "error\|warn\|fail"

# 3. Process health
ps aux | grep openclaw | head -5
```

## Step 2: Identify the Layer

| Symptom | Likely layer | Check |
|---|---|---|
| No messages at all | Gateway or channel | `openclaw status`, check bot token |
| Messages arrive but no reply | Model provider | Check API key, provider status |
| Slow responses | Model or network | Check model latency in logs |
| Cron not firing | Cron scheduler | `openclaw cron list`, check timezone |
| Memory search empty | Memory index | Check memory files exist, reindex |
| Bot says "I don't have that tool" | Tool policy | Check `tools.profile`, `tools.deny` |
| "Model not found" | Model config | Check `models.providers` in config |
| Sub-agent hangs | Sub-agent | `subagents(action="list")`, kill if stuck |

## Step 3: Layer-Specific Fixes

### Gateway Issues

```bash
# Check gateway health
openclaw gateway health

# Full diagnostics
openclaw doctor
openclaw doctor --fix    # auto-fix common issues

# Restart (interrupts sessions!)
openclaw gateway restart
```

### Model/Provider Failures

```bash
# Check which model is active
openclaw status | grep -i model

# Test model directly
openclaw agent --message "ping" --model kimi/kimi-k2.5

# View model fallback chain
cat ~/.openclaw/openclaw.json | jq '.agents.list[0].model'
```

Common model issues:
| Error | Fix |
|---|---|
| 401 Unauthorized | API key expired/wrong — check `.env` |
| 429 Rate limited | Wait, or switch to fallback model |
| 500 Server error | Provider issue — will auto-fallback |
| Timeout | Network issue or overloaded provider |
| "Model not found" | Check provider config in openclaw.json |

### Channel Issues (Telegram)

```bash
# Check Telegram connection
openclaw status | grep -i telegram

# Verify bot token
grep botToken ~/.openclaw/openclaw.json

# Check allowed senders
grep -A5 dmPolicy ~/.openclaw/openclaw.json
```

Common channel issues:
| Error | Fix |
|---|---|
| Bot doesn't respond | Check `channels.telegram.enabled` |
| "Not allowed" | Sender not in `allowFrom` or not paired |
| Messages delayed | Check `streaming` setting, network |
| Group chat ignored | Check `groupPolicy`, mention patterns |

### Cron Issues

```bash
# List all jobs
openclaw cron list

# Check run history
openclaw cron runs --id <jobId> --limit 5

# Force-run a job
openclaw cron run <jobId>
```

Common cron issues:
| Error | Fix |
|---|---|
| Never fires | Check `cron.enabled`, schedule timezone |
| Fires but no output | Check delivery mode, target channel |
| Keeps retrying | Check model — may be failing (see logs) |
| "maxConcurrentRuns" | Another job running — increase limit or wait |

### Memory Search Issues

```bash
# Check memory files exist
ls -la ~/.openclaw/workspace/memory/

# Check memory index
ls -la ~/.openclaw/memory/

# Test search
openclaw memory search --query "test"
```

Common memory issues:
| Error | Fix |
|---|---|
| Empty results | No memory files written yet |
| Stale results | Index needs refresh — write to trigger |
| "disabled" response | Check `memorySearch` config |

### Docker/VPS Issues (arifOS specific)

```bash
# Container health
docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "No docker access"

# Resource usage
free -m
df -h /
```

## Step 4: Nuclear Options (888_HOLD)

These require confirmation:

| Action | Risk | When to use |
|---|---|---|
| `openclaw gateway restart` | Drops active sessions | Gateway frozen |
| Edit `openclaw.json` | Config change | Model/channel fix needed |
| Rotate API keys | Breaks until updated | Key compromised |
| Clear sessions | Loses conversation | Corrupted session store |

## Quick Reference: Common Fixes

| Problem | One-liner fix |
|---|---|
| Gateway frozen | `openclaw gateway restart` |
| Wrong model | `/model kimi/kimi-k2.5` (in chat) |
| Cron timezone wrong | `openclaw cron edit <id> --tz "Asia/Kuala_Lumpur"` |
| Skill not loading | Check SKILL.md frontmatter, restart gateway |
| High memory | Check container limits, consider model cleanup |
| Log file huge | `> /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log` |

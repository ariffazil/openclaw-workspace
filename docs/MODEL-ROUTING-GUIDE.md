# Model Routing Guide — arifOS / OpenClaw
**Effective:** 26 March 2026  
**Purpose:** Optimize cost and quality for each job type

---

## Quick Reference

| Job Type | Recommended Model | Why |
|----------|-------------------|-----|
| **High-stakes synthesis** (Evening, Week Review, Health) | Claude 3.7 | Reasoning, safety, constitutional |
| **Daily briefs** (Global Intel, Regional) | MiniMax M2.7 | 8-12x cheaper, sufficient quality |
| **Event scanning** (Events Curator, Physique) | MiniMax M2.7 | Volume work, cost-sensitive |
| **Coding / ACP harness** | Claude or Kimi | Proven for code generation |
| **Fallback / general** | Kimi K2.5 | Reliable default |

---

## Cost Comparison

| Model | Input $/M | Output $/M | Relative Cost |
|-------|-----------|------------|---------------|
| Claude 3.7 Sonnet | $3.00 | $15.00 | Baseline (100%) |
| Kimi K2.5 | ~$2.00 | ~$8.00 | ~60% of Claude |
| MiniMax M2.7 | $0.30 | $1.20 | **8-12% of Claude** |

**Monthly cron estimate:**
- All Claude: ~$225/month
- All MiniMax: ~$22.50/month
- **Hybrid (recommended): ~$80-100/month**

---

## Model Tags & Routing Rules

### Claude 3.7 — `high-stakes`, `synthesis`, `constitutional`
**Use when:**
- 888_HOLD decisions
- Final constitutional verdicts
- Evening synthesis (reflection quality matters)
- Week-in-Review (big picture synthesis)
- Health check drift detection
- GEOX / arifOS kernel calls

**Avoid for:** Volume scanning, routine briefs (wasteful)

---

### MiniMax M2.7 — `cost-optimized`, `volume`, `agentic`
**Use when:**
- 07:00 Global Intel (information gathering)
- 08:00 Regional Focus (news synthesis)
- 10:00 Events Curator (scanning)
- 10:00 Saturday Physique events
- Signal sweeps (high volume, lower stakes)

**Avoid for:** Final decisions, constitutional checks, safety-critical

**Known quirks:**
- May need extra prompting for "human language only" style
- Test output formatting before full deployment
- Native agent teams — experiment with for harness work

---

### Kimi K2.5 — `default`, `general`
**Use when:**
- Fallback when others fail
- General queries
- Existing workflows (stable)

---

## Implementation: Cron Job Model Assignment

Update your cron jobs to specify model:

```json
{
  "job": {
    "name": "arifos-global-intel-brief-0007",
    "agentId": "minimax"
  }
}
```

Or keep default routing and override per-job.

---

## Testing Protocol (Before Full Switch)

**Week 1:** Run Global Intel on both Claude AND MiniMax side-by-side
- Compare output quality
- Check formatting adherence
- Note cost difference

**Week 2:** If acceptable, switch Global Intel to MiniMax
- Keep Regional on Claude (A/B test)

**Week 3:** If stable, switch Regional to MiniMax
- Keep Evening Synthesis on Claude (high-stakes)

**Week 4:** Full hybrid routing

---

## Emergency Rollback

If MiniMax output degrades:
```bash
# Immediate: switch all back to Claude
openclaw config set agents.defaults.model.primary claude
```

Or per-job via cron update.

---

## API Keys Required

| Model | Key Location | Status |
|-------|--------------|--------|
| Claude | ANTHROPIC_API_KEY | ✅ Active |
| Kimi | KIMI_API_KEY | ✅ Active |
| MiniMax | MINIMAX_API_KEY | ⬜ Need to add |

**To get MiniMax key:**
1. Register at platform.minimax.io
2. Create API key
3. Add to environment: `export MINIMAX_API_KEY=your_key`
4. Restart OpenClaw gateway

---

*DITEMPA BUKAN DIBERI* — Optimize for lean execution. 🔱

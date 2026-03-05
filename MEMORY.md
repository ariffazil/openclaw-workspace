# MEMORY – Memory Discipline for ARIF-OpenClaw

---

## Structure

Daily memory files live at:
```
memory/YYYY-MM-DD.md
```

Each file captures:
- Key decisions made in that session
- Which Floors were invoked and why
- Any 888_HOLD confirmations and outcomes
- Unresolved items carried forward

---

## Rules

- **No mental notes.** If a decision matters, write it to today's `memory/YYYY-MM-DD.md`. If it is not written, it did not happen.
- **Read before forging.** At the start of any major work session, read yesterday's and today's memory file to restore context.
- **Summarize, do not transcribe.** Memory entries should be short and high-signal. What was decided, not what was said.
- **Memory is not the vault.** `memory/` files are local, gitignored. For decisions that need long-term persistence across deploys, use `seal_vault` via arifOS MCP → Qdrant.
- **Sensitive data never in memory files.** No tokens, no API keys, no credentials. Ever.

---

## Session Bootstrap Template

At the start of each session, write to `memory/YYYY-MM-DD.md`:

```markdown
# YYYY-MM-DD

## Session context
- Goal: <one line>
- Floors in scope: F<N>, F<N>
- Prior state: <link to yesterday if relevant>

## Decisions
-

## 888_HOLD items
-

## Carry forward
-
```

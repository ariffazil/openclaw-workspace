# Constitutional Git Worktree Toolchain

**Status:** ✅ IMPLEMENTED  
**Version:** 2026.03.24  
**Floors:** F1-F13 enforced at filesystem level

---

## What Was Forged

This toolchain implements **constitutional governance for AI agent development** using git worktrees as the enforcement layer.

### Files Created

| File | Purpose | Floors Enforced | Language |
|------|---------|-----------------|----------|
| `arifos-worktree-add.sh` | Create F1-compliant agent sandbox | F1, F2, F4, F11, F12 | Bash |
| `arifos-worktree-remove.sh` | Collapse rejected universe → VOID | F1 | Bash |
| `arifos-agent-run.sh` | Run agent under F1-F3 contract | F2, F7, F11 | Bash |
| `arifos-f3-eval.sh` | Tri-Witness pre-flight check (bash) | F3 | Bash |
| `arifos_f3_eval.py` | **Tri-Witness CLI (PyPI-ready)** | F3 | Python |
| `templates/arifos.yml.template` | Constitutional manifest schema | F3 | YAML |
| `.github/workflows/888-judge.yml` | PR = 888_JUDGE enforcement | F1-F4, F7, F11-F12 | YAML |

---

## Quick Start

```bash
# 1. Add to PATH or run directly
export PATH="$PATH:$(pwd)"

# 2. Create constitutional sandbox for Claude
cd /mnt/arifos
~/workspace/arifos-worktree-add.sh claude mcp-hardening

# 3. Enter sandbox and run F3 evaluation
cd ../arifos-worktrees/arifos-claude-mcp-hardening
~/workspace/arifos_f3_eval.py --worktree . --pr-draft

# 4. When SEAL achieved, commit and push
git add .
git commit -m "feat: mcp hardening with F1-F13 compliance"
git push origin feature/claude-mcp-hardening

# 5. Open PR → 888_JUDGE runs automatically
# 6. If rejected, collapse universe:
~/workspace/arifos-worktree-remove.sh feature/claude-mcp-hardening
```

---

## Constitutional Architecture

```
/mnt/arifos/                    # Main worktree — THE VAULT (main)
├── 0_KERNEL/                   # Constitutional law — read-only
├── scripts/
│   └── arifos-worktree-*.sh   # Bash toolchain
├── arifos_f3_eval.py          # Python CLI (PyPI)
└── ...

/mnt/arifos-worktrees/          # Parallel universes
├── arifos-claude-mcp-hardening/    # Claude's sandbox
│   ├── arifos.yml              # Constitutional manifest
│   └── ...
├── arifos-codex-api-refactor/      # Codex's sandbox
└── arifos-hotfix-critical/         # Emergency worktree (F13 only)
```

---

## F1-F13 Mapping

| Floor | Git Worktree Enforcement |
|-------|-------------------------|
| **F1** | `git worktree remove` = full reversibility |
| **F2** | `main` branch locked — PR required |
| **F3** | `arifos_f3_eval.py` — Tri-Witness evaluation |
| **F4** | Naming: `arifos-{agent}-{feature}` |
| **F5** | `git worktree list` shows all states |
| **F6** | Agent worktrees isolated |
| **F7** | `dry_run` mode by default |
| **F8** | `arifos-experiment/` for radical ideas |
| **F9** | Agents can't claim authorship |
| **F10** | Worktrees are directories, not "agents" |
| **F11** | Hotfix worktree = HOLD_888 |
| **F12** | `.gitignore` enforces no secrets |
| **F13** | Arif holds merge rights to `main` |

---

## Python CLI: arifos_f3_eval.py

### Installation
```bash
# Copy to arifos package
pip install pyyaml  # Optional, for manifest updates
./arifos_f3_eval.py --help
```

### Usage
```bash
# Basic evaluation
./arifos_f3_eval.py --worktree .

# With JSON output
./arifos_f3_eval.py --json

# Enforce strict mode (exit 1 on VOID)
./arifos_f3_eval.py --enforce

# Update manifest with results
./arifos_f3_eval.py --update-manifest
```

### Example Output
```
🔥 F3 TRI-WITNESS EVALUATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Worktree: /mnt/arifos-worktrees/arifos-claude-mcp-hardening
🤖 Agent:    claude
⚠️  Risk:     medium

🤖 AI WITNESS (Agent Self-Check)
─────────────────────────────────────────
   Score: 0.87

🌍 EARTH WITNESS (Local Validation)
─────────────────────────────────────────
   Score: 0.92

👤 HUMAN WITNESS (Review)
─────────────────────────────────────────
   Score: 0.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️  TRI-WITNESS CONSENSUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   W₃ = (0.0 × 0.87 × 0.92)^(1/3)
   W₃ = 0.0

   Threshold (medium): 0.95

   🚨 VERDICT: HOLD_888

   F13 REQUIRED: Arif must review personally
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## The 888_JUDGE PR Template

When opening a PR, include this checklist:

```markdown
## Constitutional Review Checklist

- [ ] **F1**: Can this be reverted? (`git revert` tested)
- [ ] **F2**: τ ≥ 0.99? (Tests pass, docs updated)
- [ ] **F3**: Tri-Witness? (Human + AI + Earth)
- [ ] **F4**: ΔS ≤ 0? (Reduces confusion)
- [ ] **F7**: Ω₀ stated? (Uncertainty acknowledged)

**Verdict:** [ ] SEAL  [ ] SABAR  [ ] HOLD_888  [ ] VOID
```

---

## arifos.yml Schema

Each worktree contains a manifest:

```yaml
arifos_version: "2026.03.24"
worktree:
  id: "arifos-claude-mcp-hardening"
  branch: "feature/claude-mcp-hardening"
  parent: "main"
  
agent:
  name: "claude"
  type: "coding"
  runtime: "acp"
  
constitutional:
  floors: [F1, F2, F4, F11]
  veto_holder: "arif"
  max_risk_tier: "medium"
  dry_run: true
  
governance:
  tri_witness:
    human: "pending"
    ai: "pending"
    earth: "pending"
  verdict: "SABAR"
  
vault:
  lineage: true
  ttl_days: 30
```

---

## Next Steps

1. **Install** scripts to `/mnt/arifos/scripts/`
2. **Add** `arifos_f3_eval.py` to PyPI package
3. **Configure** GitHub branch protection for `main`
4. **Test** with a real agent worktree
5. **Document** in arifOS repo

---

*Ditempa bukan diberi.* 🔥

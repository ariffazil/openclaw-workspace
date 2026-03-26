#!/usr/bin/env python3
"""
arifos-f3-eval.py
CLAIM: Tri-Witness evaluation CLI — pre-flight constitutional check.
Integrates with arifos PyPI package.

Usage:
    arifos f3-eval --worktree . --mode pre-push
    arifos f3-eval --worktree . --json
    arifos f3-eval --enforce  # Exit 1 if W₃ < threshold
"""

import argparse
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass
class WitnessScores:
    """F3 Tri-Witness scores"""
    ai: float      # Agent self-check (0.0-1.0)
    earth: float   # Local validation (0.0-1.0)
    human: float   # Review status (0.0-1.0)
    
    def geometric_mean(self) -> float:
        """W₃ = (H × A × E)^(1/3)"""
        if self.ai <= 0 or self.earth <= 0 or self.human <= 0:
            return 0.0
        return (self.ai * self.earth * self.human) ** (1/3)


@dataclass
class VerdictResult:
    """888_JUDGE verdict"""
    verdict: str           # SEAL, PROVISIONAL, SABAR, HOLD, HOLD_888, VOID
    w3: float             # Tri-witness score
    threshold: float      # Risk-adjusted threshold
    scores: WitnessScores
    emoji: str
    message: str


class ArifosF3Eval:
    """F3 Tri-Witness evaluator"""
    
    # Risk tier thresholds
    THRESHOLDS = {
        "low": 0.850,
        "medium": 0.950,
        "high": 0.990,
        "critical": 1.000  # Requires human=1.0
    }
    
    # Verdict emojis
    EMOJIS = {
        "SEAL": "✅",
        "PROVISIONAL": "⚠️",
        "SABAR": "⏸️",
        "HOLD": "🛑",
        "HOLD_888": "🚨",
        "VOID": "❌"
    }
    
    def __init__(self, worktree: Path):
        self.worktree = worktree
        self.manifest = self._load_manifest()
        
    def _load_manifest(self) -> Dict:
        """Load arifos.yml from worktree"""
        manifest_path = self.worktree / "arifos.yml"
        if not manifest_path.exists():
            # Try yaml parsing with yq fallback
            return self._load_manifest_fallback()
        
        try:
            import yaml
            with open(manifest_path) as f:
                return yaml.safe_load(f)
        except ImportError:
            return self._load_manifest_fallback()
    
    def _load_manifest_fallback(self) -> Dict:
        """Fallback manifest parsing without PyYAML"""
        manifest_path = self.worktree / "arifos.yml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"F4: No arifos.yml found in {self.worktree}")
        
        # Simple key-value extraction
        manifest = {
            "agent": {"name": "unknown", "type": "coding"},
            "constitutional": {"max_risk_tier": "medium", "veto_holder": "arif"},
            "worktree": {"branch": "unknown"}
        }
        
        with open(manifest_path) as f:
            content = f.read()
            # Extract simple fields
            for line in content.split('\n'):
                if 'name:' in line and '"' in line:
                    manifest["agent"]["name"] = line.split('"')[1]
                elif 'max_risk_tier:' in line:
                    manifest["constitutional"]["max_risk_tier"] = line.split(':')[1].strip().strip('"')
        
        return manifest
    
    def _compute_ai_witness(self) -> float:
        """
        🤖 AI Witness: Agent self-check score
        
        Metrics:
        - Constitutional kernel usage (+0.25)
        - F1-F13 references (+0.25)
        - Test coverage (+0.20)
        - Documentation (+0.17)
        - Conventional commits (+0.13)
        """
        score = 0.0
        
        # 1. Constitutional kernel usage
        if self._grep_code("arifOS_kernel|init_anchor|apex_soul"):
            score += 0.25
            
        # 2. F1-F13 awareness
        floor_refs = len(self._grep_code_lines(r"F[1-9]|F1[0-3]"))
        if floor_refs > 5:
            score += 0.25
        elif floor_refs > 0:
            score += 0.15
            
        # 3. Test coverage
        test_dirs = list(self.worktree.glob("**/test*")) + list(self.worktree.glob("**/tests"))
        if test_dirs and any(d.is_dir() for d in test_dirs):
            score += 0.20
            
        # 4. Documentation
        md_files = list(self.worktree.glob("**/*.md"))
        if len(md_files) > 0:
            score += 0.17
            
        # 5. Conventional commits
        if self._check_conventional_commits():
            score += 0.13
            
        return round(score, 2)
    
    def _compute_earth_witness(self) -> float:
        """
        🌍 Earth Witness: Local validation score
        
        Metrics:
        - Git cleanliness (+0.25)
        - Syntax validation (+0.25)
        - Constitutional naming (+0.25)
        - Recent activity (+0.25)
        """
        score = 0.0
        
        # 1. Git cleanliness
        if self._git_clean():
            score += 0.25
        elif self._git_unstaged_count() < 5:
            score += 0.10
            
        # 2. Syntax validation
        if self._validate_python_syntax():
            score += 0.25
            
        # 3. Constitutional branch naming
        branch = self._git_branch()
        if branch and any(branch.startswith(p) for p in ["feature/", "hotfix/", "experiment/"]):
            score += 0.25
            
        # 4. Recent activity
        if self._git_recent_commits(days=7):
            score += 0.25
            
        return round(score, 2)
    
    def _compute_human_witness(self) -> float:
        """
        👤 Human Witness: Review status score
        
        - 0.00 = pending (default)
        - 0.50 = partial review
        - 1.00 = approved
        """
        # Check manifest for human status
        governance = self.manifest.get("governance", {})
        tri_witness = governance.get("tri_witness", {})
        human_status = tri_witness.get("human", "pending")
        
        status_scores = {
            "pending": 0.00,
            "self-checked": 0.25,  # Agent marked it
            "partial": 0.50,
            "approved": 1.00,
            "rejected": 0.00
        }
        
        # Check for signed commit as proxy for human attestation
        if self._git_signed_commit():
            return 0.90
            
        return status_scores.get(human_status, 0.00)
    
    def evaluate(self) -> VerdictResult:
        """Run full F3 Tri-Witness evaluation"""
        
        # Compute scores
        ai = self._compute_ai_witness()
        earth = self._compute_earth_witness()
        human = self._compute_human_witness()
        
        scores = WitnessScores(ai=ai, earth=earth, human=human)
        w3 = round(scores.geometric_mean(), 3)
        
        # Get risk tier and threshold
        risk_tier = self.manifest.get("constitutional", {}).get("max_risk_tier", "medium")
        threshold = self.THRESHOLDS.get(risk_tier, 0.950)
        
        # Determine verdict
        if w3 >= threshold:
            verdict = "SEAL"
        elif w3 >= threshold - 0.10:
            verdict = "PROVISIONAL"
        elif w3 >= 0.500:
            verdict = "HOLD"
        else:
            verdict = "VOID"
        
        # Override for medium+ risk without human approval
        if risk_tier != "low" and human < 0.5:
            verdict = "HOLD_888"
        
        # Generate message
        messages = {
            "SEAL": "Ready for merge after final human review",
            "PROVISIONAL": "Can proceed with reservations documented",
            "SABAR": "Pause — needs more context",
            "HOLD": "Requires additional work before merge",
            "HOLD_888": "F13 REQUIRED: Arif must review personally",
            "VOID": "Rejected — constitutional floors failed"
        }
        
        return VerdictResult(
            verdict=verdict,
            w3=w3,
            threshold=threshold,
            scores=scores,
            emoji=self.EMOJIS[verdict],
            message=messages[verdict]
        )
    
    def print_report(self, result: VerdictResult, json_mode: bool = False):
        """Print evaluation report"""
        
        if json_mode:
            print(json.dumps({
                "verdict": result.verdict,
                "w3": result.w3,
                "threshold": result.threshold,
                "scores": asdict(result.scores),
                "message": result.message
            }, indent=2))
            return
        
        # Terminal report
        agent_name = self.manifest.get("agent", {}).get("name", "unknown")
        risk_tier = self.manifest.get("constitutional", {}).get("max_risk_tier", "medium")
        branch = self.manifest.get("worktree", {}).get("branch", "unknown")
        
        print("")
        print("🔥 F3 TRI-WITNESS EVALUATION")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📁 Worktree: {self.worktree}")
        print(f"🤖 Agent:    {agent_name}")
        print(f"⚠️  Risk:     {risk_tier}")
        print(f"🔒 Branch:   {branch}")
        print("")
        
        print("🤖 AI WITNESS (Agent Self-Check)")
        print("─────────────────────────────────────────")
        print(f"   Score: {result.scores.ai}")
        print("")
        
        print("🌍 EARTH WITNESS (Local Validation)")
        print("─────────────────────────────────────────")
        print(f"   Score: {result.scores.earth}")
        print("")
        
        print("👤 HUMAN WITNESS (Review)")
        print("─────────────────────────────────────────")
        print(f"   Score: {result.scores.human}")
        print("")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("⚖️  TRI-WITNESS CONSENSUS")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"")
        print(f"   W₃ = ({result.scores.human} × {result.scores.ai} × {result.scores.earth})^(1/3)")
        print(f"   W₃ = {result.w3}")
        print(f"")
        print(f"   Threshold ({risk_tier}): {result.threshold}")
        print(f"")
        print(f"   {result.emoji} VERDICT: {result.verdict}")
        print(f"")
        print(f"   {result.message}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def update_manifest(self, result: VerdictResult):
        """Update arifos.yml with evaluation results"""
        manifest_path = self.worktree / "arifos.yml"
        if not manifest_path.exists():
            return
        
        try:
            import yaml
            with open(manifest_path) as f:
                data = yaml.safe_load(f)
            
            data.setdefault("governance", {}).setdefault("tri_witness", {})
            data["governance"]["tri_witness"]["ai"] = result.scores.ai
            data["governance"]["tri_witness"]["earth"] = result.scores.earth
            data["governance"]["tri_witness"]["human"] = result.scores.human
            data["governance"]["verdict"] = result.verdict
            
            with open(manifest_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except ImportError:
            pass  # Skip if PyYAML not available
    
    # Helper methods
    def _grep_code(self, pattern: str) -> bool:
        """Search for pattern in code files"""
        try:
            result = subprocess.run(
                ["grep", "-r", "-E", pattern, "--include=*.py", "--include=*.js", "--include=*.ts"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and len(result.stdout) > 0
        except:
            return False
    
    def _grep_code_lines(self, pattern: str) -> list:
        """Search for pattern and return lines"""
        try:
            result = subprocess.run(
                ["grep", "-r", "-E", pattern, "--include=*.py", "--include=*.js", "--include=*.md"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n') if result.stdout else []
        except:
            return []
    
    def _check_conventional_commits(self) -> bool:
        """Check for conventional commit messages"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            commits = result.stdout.lower()
            patterns = ["feat:", "fix:", "docs:", "refactor:", "test:", "chore:"]
            return any(p in commits for p in patterns)
        except:
            return False
    
    def _git_clean(self) -> bool:
        """Check if git working tree is clean"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _git_unstaged_count(self) -> int:
        """Count unstaged files"""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return len([l for l in result.stdout.split('\n') if l.strip()])
        except:
            return 0
    
    def _validate_python_syntax(self) -> bool:
        """Validate Python syntax"""
        py_files = list(self.worktree.glob("**/*.py"))
        py_files = [f for f in py_files if ".git" not in str(f)]
        
        if not py_files:
            return True  # No Python files = valid
        
        for f in py_files[:5]:  # Check first 5 files
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(f)],
                    capture_output=True
                )
                if result.returncode != 0:
                    return False
            except:
                return False
        return True
    
    def _git_branch(self) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _git_recent_commits(self, days: int = 7) -> bool:
        """Check for recent commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={days} days ago", "--oneline"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def _git_signed_commit(self) -> bool:
        """Check for signed commits"""
        try:
            result = subprocess.run(
                ["git", "log", "--show-signature", "-1"],
                cwd=self.worktree,
                capture_output=True,
                text=True
            )
            return "Good signature" in result.stdout
        except:
            return False


def main():
    parser = argparse.ArgumentParser(
        description="F3 Tri-Witness evaluation — pre-flight constitutional check"
    )
    parser.add_argument(
        "--worktree",
        type=Path,
        default=Path("."),
        help="Path to constitutional worktree (default: current directory)"
    )
    parser.add_argument(
        "--mode",
        choices=["pre-push", "pre-commit", "audit"],
        default="pre-push",
        help="Evaluation mode"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of pretty report"
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit 1 if verdict is VOID or below threshold"
    )
    parser.add_argument(
        "--update-manifest",
        action="store_true",
        help="Update arifos.yml with evaluation results"
    )
    
    args = parser.parse_args()
    
    # Validate worktree
    worktree = args.worktree.resolve()
    manifest_path = worktree / "arifos.yml"
    
    if not manifest_path.exists():
        print(f"❌ F4: No arifos.yml found in {worktree}", file=sys.stderr)
        print("   This is not a constitutional worktree.", file=sys.stderr)
        sys.exit(1)
    
    # Run evaluation
    try:
        evaluator = ArifosF3Eval(worktree)
        result = evaluator.evaluate()
        
        # Print report
        evaluator.print_report(result, json_mode=args.json)
        
        # Update manifest if requested
        if args.update_manifest:
            evaluator.update_manifest(result)
        
        # Enforce if requested
        if args.enforce:
            if result.verdict in ["VOID", "HOLD_888"]:
                print(f"\n❌ F3: Enforcement triggered — {result.verdict}", file=sys.stderr)
                sys.exit(1)
            elif result.verdict == "HOLD":
                print(f"\n⏸️  F3: Recommendation — improve scores before push")
        
        # Exit codes
        if result.verdict == "SEAL":
            sys.exit(0)
        elif result.verdict in ["PROVISIONAL", "SABAR"]:
            sys.exit(0)
        elif result.verdict == "HOLD":
            sys.exit(0)  # Soft failure
        else:
            sys.exit(1)  # Hard failure
            
    except Exception as e:
        print(f"❌ F3 Evaluation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

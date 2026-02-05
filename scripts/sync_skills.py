#!/usr/bin/env python3
"""Sync .agent/skills and .claude/skills.

Rules:
- Union of skills in both locations is kept.
- When a skill exists in both, the preferred side wins (default: .agent).
- Files are copied recursively; deletions are NOT propagated.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".agent/skills"
CLAUDE = ROOT / ".claude/skills"


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def trees_equal(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return False
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False
    return all(trees_equal(a / name, b / name) for name in cmp.common_dirs)


def sync(prefer: str) -> None:
    AGENT.mkdir(parents=True, exist_ok=True)
    CLAUDE.mkdir(parents=True, exist_ok=True)

    agent_skills = {p.name: p for p in AGENT.iterdir() if p.is_dir()}
    claude_skills = {p.name: p for p in CLAUDE.iterdir() if p.is_dir()}

    all_names = sorted(set(agent_skills) | set(claude_skills))

    for name in all_names:
        a = agent_skills.get(name)
        c = claude_skills.get(name)

        if a and c:
            if trees_equal(a, c):
                continue
            if prefer == "agent":
                copy_tree(a, c)
            else:
                copy_tree(c, a)
        elif a and not c:
            copy_tree(a, CLAUDE / name)
        elif c and not a:
            copy_tree(c, AGENT / name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync .agent/skills and .claude/skills")
    parser.add_argument("--prefer", choices=["agent", "claude"], default="agent")
    args = parser.parse_args()

    sync(args.prefer)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Ingest Claude Code-generated JSON into Obsidian vault.

Supports:
- Single JSON file containing {paper, analysis}
- JSON array of {paper, analysis} objects
- Directory of paper_*.json files
"""
from __future__ import annotations

import argparse
import os
import json
from datetime import datetime
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
LPDD = ROOT / "lpdd"
sys.path.insert(0, str(LPDD))

from writer import write_from_json, write_daily_from_json  # noqa: E402
import yaml  # noqa: E402


def load_items(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.glob("paper_*.json"))
    return []


def normalize_to_array(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return [data]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Claude JSON into Obsidian")
    parser.add_argument("--json", type=str, help="JSON file path")
    parser.add_argument("--dir", type=str, default="/tmp", help="Directory with paper_*.json")
    parser.add_argument("--date", type=str, help="Daily summary date (YYYY-MM-DD)")
    parser.add_argument("--vault", type=str, help="Obsidian vault path")
    args = parser.parse_args()

    targets = []
    if args.json:
        targets = load_items(Path(args.json))
    else:
        targets = load_items(Path(args.dir))

    if not targets:
        raise SystemExit("No JSON files found")

    all_items: list[dict] = []

    # resolve vault path
    env_vault = os.environ.get("OBSIDIAN_VAULT_PATH")
    if args.vault:
        vault_path = Path(args.vault).expanduser()
    elif env_vault:
        vault_path = Path(env_vault).expanduser()
    else:
        config_path = LPDD / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        vault_path = Path(config["obsidian"]["vault_path"]).expanduser()
        if not vault_path.exists():
            # fallback to repo root if config points to a non-existent path
            vault_path = ROOT

    for path in targets:
        items = normalize_to_array(path)
        all_items.extend(items)

        for item in items:
            tmp_path = path
            if len(items) > 1:
                tmp_path = Path("/tmp") / f"paper_{item['paper']['arxiv_id']}.json"
                tmp_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
            write_from_json(
                json_path=str(tmp_path),
                vault_path=vault_path,
                templates_dir=str(LPDD / "templates"),
            )

    date = args.date or datetime.now().strftime("%Y-%m-%d")
    merged_path = Path("/tmp/claude_digest.json")
    merged_path.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    write_daily_from_json(
        json_path=str(merged_path),
        date=date,
        vault_path=vault_path,
        templates_dir=str(LPDD / "templates"),
    )

    print(f"Wrote {len(all_items)} papers, daily summary {date}")


if __name__ == "__main__":
    main()

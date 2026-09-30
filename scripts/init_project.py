#!/usr/bin/env python3
"""Create a user project from public starter presets without modifying this source tree."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PRESET = ROOT / "presets" / "starter"
FILES = ("account-profile.yaml", "project-config.yaml", "keyword-catalog.yaml", "visual-config.yaml")

def initialize(destination: Path) -> Path:
    target = destination.expanduser().resolve()
    if target.exists():
        raise FileExistsError(f"目标已存在，为避免覆盖已停止：{target}")
    missing = [name for name in FILES if not (PRESET / name).is_file()]
    if missing:
        raise FileNotFoundError(f"缺少 Starter Preset：{', '.join(missing)}")
    config = target / "config"
    config.mkdir(parents=True)
    for name in FILES:
        shutil.copyfile(PRESET / name, config / name)
    for folder in ("workspace", "outputs", "learning"):
        (target / folder).mkdir()
    return target

def main() -> int:
    parser = argparse.ArgumentParser(description="初始化个人小红书 Skills 项目")
    parser.add_argument("--destination", type=Path, default=Path.cwd() / "user-project")
    args = parser.parse_args()
    try:
        target = initialize(args.destination)
    except (FileExistsError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 1
    print(f"PROJECT INITIALIZED: {target}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

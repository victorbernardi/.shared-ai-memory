#!/usr/bin/env python3
"""Transactional global installation of rendered skill packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "stout-create-skill" / "scripts"))
from platform_contract import SUPPORTED_PLATFORMS


@dataclass(frozen=True)
class GlobalTarget:
    platform: str
    path: Path


@dataclass(frozen=True)
class InstallResult:
    status: str
    installed: dict[str, str]
    message: str


def load_global_targets(config_path: Path) -> dict[str, GlobalTarget]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    targets = {}
    for platform, raw_path in data.get("targets", {}).items():
        resolved = os.path.expandvars(raw_path)
        targets[platform] = GlobalTarget(platform=platform, path=Path(resolved))
    return targets


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _dir_hash(directory: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(directory.rglob("*")):
        if f.is_file():
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _backup_destination(dest: Path, backup_dir: Path) -> Path:
    backup = backup_dir / dest.name
    if backup.exists():
        if backup.is_dir():
            shutil.rmtree(backup)
        else:
            backup.unlink()
    if dest.is_dir():
        shutil.copytree(dest, backup)
    else:
        shutil.copy2(dest, backup)
    return backup


def install_artifacts(
    source_dir: Path,
    artifacts_dir: Path,
    targets: tuple[str, ...],
    replace: bool,
    global_targets: dict[str, GlobalTarget],
) -> dict:
    result = {"status": "ok", "installed": {}, "rolled_back": False, "message": ""}

    backups: dict[str, Path] = {}
    created_now: list[str] = []
    backup_dir = Path(tempfile.mkdtemp(prefix="stout-backup-"))
    skill_name = source_dir.name

    try:
        for platform in targets:
            if platform not in global_targets:
                result["status"] = "error"
                result["message"] = f"Plataforma '{platform}' nao configurada"
                return result

            target = global_targets[platform]
            dest = target.path / skill_name

            if dest.exists() and not replace:
                result["status"] = "collision"
                result["message"] = f"Destino ja existe: {dest}. Use --replace para sobrescrever."
                return result

            if dest.exists() and replace:
                backups[platform] = _backup_destination(dest, backup_dir)

        for platform in targets:
            target = global_targets[platform]
            dest = target.path / skill_name
            rendered = artifacts_dir / "rendered" / platform / skill_name

            if not rendered.exists():
                result["status"] = "error"
                result["message"] = f"Pacote renderizado nao encontrado: {rendered}"
                _rollback(backups, created_now, global_targets, skill_name)
                result["rolled_back"] = True
                return result

            try:
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.copytree(rendered, dest)
                result["installed"][platform] = str(dest)
                if platform not in backups:
                    created_now.append(platform)
            except Exception as exc:
                result["status"] = "error"
                result["message"] = f"Falha ao copiar para {platform}: {exc}"
                _rollback(backups, created_now, global_targets, skill_name)
                result["rolled_back"] = True
                return result

        install_record = {
            "skill_name": skill_name,
            "installed_at": time.time(),
            "targets": result["installed"],
            "hashes": {},
        }
        for platform, path_str in result["installed"].items():
            install_record["hashes"][platform] = _dir_hash(Path(path_str))

        install_json = source_dir / ".stout-install.json"
        install_json.write_text(
            json.dumps(install_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return result

    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)


def _rollback(
    backups: dict[str, Path],
    created_now: list[str],
    global_targets: dict[str, GlobalTarget],
    skill_name: str,
) -> None:
    for platform in created_now:
        if platform not in backups:
            target = global_targets[platform]
            dest = target.path / skill_name
            try:
                if dest.is_dir():
                    shutil.rmtree(dest)
                elif dest.exists():
                    dest.unlink()
            except Exception:
                pass

    for platform, backup_path in backups.items():
        target = global_targets[platform]
        dest = target.path / skill_name
        try:
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(backup_path), str(dest))
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Install rendered packages globally")
    parser.add_argument("--source-path", type=str, required=True, help="Canonical skill source")
    parser.add_argument("--artifacts-dir", type=str, required=True, help="Rendered artifacts directory")
    parser.add_argument("--targets", type=str, default=None, help="Comma-separated platforms (default: all)")
    parser.add_argument("--replace", action="store_true", help="Replace existing destinations")
    parser.add_argument("--config", type=str, default=None, help="Path to global_targets.yaml")
    args = parser.parse_args()

    source_dir = Path(args.source_path)
    artifacts_dir = Path(args.artifacts_dir)

    config_path = Path(args.config) if args.config else (
        Path(__file__).parent.parent / "config" / "global_targets.yaml"
    )
    global_targets = load_global_targets(config_path)

    if args.targets:
        selected = tuple(t.strip() for t in args.targets.split(",") if t.strip())
    else:
        selected = SUPPORTED_PLATFORMS

    result = install_artifacts(source_dir, artifacts_dir, selected, args.replace, global_targets)

    if result["status"] == "ok":
        print(f"[OK] Instalacao concluida: {result['installed']}")
    elif result["status"] == "collision":
        print(f"[COLISAO] {result['message']}", file=sys.stderr)
        sys.exit(1)
    elif result["rolled_back"]:
        print(f"[ROLLBACK] {result['message']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[ERRO] {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

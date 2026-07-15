#!/usr/bin/env python3
"""Shared platform IDs, manifest parsing, capability catalog parsing, and report models."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal
import json
import yaml

SUPPORTED_PLATFORMS: tuple[str, ...] = ("codex", "claude-code", "commandcode")


@dataclass(frozen=True)
class PlatformManifest:
    targets: tuple[str, ...]
    extensions: tuple[ExtensionRequest, ...]


@dataclass(frozen=True)
class ExtensionRequest:
    id: str
    required: bool
    value: str | list[str] | dict


@dataclass(frozen=True)
class CompatibilityItem:
    extension_id: str
    platform: str
    status: Literal["included", "skipped", "error"]
    reason: str


def parse_targets(value: str | None) -> tuple[str, ...]:
    targets = SUPPORTED_PLATFORMS if value is None else tuple(
        p.strip() for p in value.split(",") if p.strip()
    )
    invalid = set(targets) - set(SUPPORTED_PLATFORMS)
    if invalid or not targets:
        raise ValueError(f"targets invalidos: {', '.join(sorted(invalid))}")
    return targets


def create_default_manifest(targets: tuple[str, ...] = SUPPORTED_PLATFORMS) -> dict:
    return {"targets": list(targets), "extensions": []}


def load_manifest(path: Path) -> PlatformManifest:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    extensions = tuple(
        ExtensionRequest(
            id=ext["id"],
            required=ext.get("required", False),
            value=ext.get("value", ""),
        )
        for ext in data.get("extensions", [])
    )
    return PlatformManifest(
        targets=tuple(data.get("targets", list(SUPPORTED_PLATFORMS))),
        extensions=extensions,
    )


def load_catalog(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

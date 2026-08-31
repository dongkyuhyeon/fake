#!/usr/bin/env python3
"""Validate the downloaded BEATs checkpoint without constructing the model."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import torch


DEFAULT_PATH = Path("/workspace/model_artifacts/beats/BEATs_iter3_plus_AS2M.pt")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as checkpoint:
        for chunk in iter(lambda: checkpoint.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not path.is_file():
        raise SystemExit(f"checkpoint not found: {path}")

    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        checkpoint = torch.load(path, map_location="cpu")

    if not isinstance(checkpoint, dict):
        raise SystemExit("invalid checkpoint: top-level object is not a dict")
    missing = {"cfg", "model"}.difference(checkpoint)
    if missing:
        raise SystemExit(f"invalid checkpoint: missing keys {sorted(missing)}")

    print(f"path: {path}")
    print(f"size: {path.stat().st_size} bytes")
    print(f"sha256: {sha256(path)}")
    print("required keys: OK (cfg, model)")


if __name__ == "__main__":
    main()

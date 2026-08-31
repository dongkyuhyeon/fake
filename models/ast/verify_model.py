#!/usr/bin/env python3
"""Verify AST files and confirm that Transformers can load them offline."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from transformers import AutoFeatureExtractor, AutoModelForAudioClassification


DEFAULT_DIRECTORY = Path("/workspace/model_artifacts/ast")
EXPECTED_SHA256 = "ae0c1e2ad4e1381d851fa9bf298ba13ebc9c5a914cdee2dbe427a6583869924d"
REQUIRED_FILES = ("config.json", "preprocessor_config.json", "model.safetensors")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY
    missing = [name for name in REQUIRED_FILES if not (directory / name).is_file()]
    if missing:
        raise SystemExit(f"missing model files: {missing}")

    weights = directory / "model.safetensors"
    actual_sha256 = sha256(weights)
    if actual_sha256 != EXPECTED_SHA256:
        raise SystemExit(f"weight checksum mismatch: {actual_sha256}")

    extractor = AutoFeatureExtractor.from_pretrained(directory, local_files_only=True)
    model = AutoModelForAudioClassification.from_pretrained(
        directory,
        local_files_only=True,
        use_safetensors=True,
    )
    print(f"weights sha256: {actual_sha256}")
    print(f"labels: {model.config.num_labels}")
    print(f"sampling rate: {extractor.sampling_rate}")
    print("offline load: OK")


if __name__ == "__main__":
    main()

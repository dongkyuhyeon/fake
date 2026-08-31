#!/usr/bin/env python3
"""Download the pinned AST files needed for offline inference."""

from __future__ import annotations

import sys
from pathlib import Path

from huggingface_hub import snapshot_download


MODEL_ID = "MIT/ast-finetuned-audioset-10-10-0.4593"
REVISION = "f826b80d28226b62986cc218e5cec390b1096902"
DEFAULT_DIRECTORY = Path("/workspace/model_artifacts/ast")
REQUIRED_FILES = ("config.json", "preprocessor_config.json", "model.safetensors")


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY
    destination.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=MODEL_ID,
        revision=REVISION,
        local_dir=destination,
        allow_patterns=list(REQUIRED_FILES),
    )
    print(f"model directory: {destination}")


if __name__ == "__main__":
    main()

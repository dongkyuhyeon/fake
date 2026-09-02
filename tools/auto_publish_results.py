#!/usr/bin/env python
"""Safely publish experiment-result changes from this repository to GitHub.

Only changes below experiments/ are staged. Model weights, archives, secrets,
and oversized files are blocked. The script stays silent when there is nothing
to publish, which makes it suitable for a scheduler watchdog.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ALLOWED_ROOT = "experiments"
MAX_FILE_BYTES = 95 * 1024 * 1024
BLOCKED_SUFFIXES = {
    ".bin", ".pth", ".pt", ".th", ".ckpt", ".safetensors",
    ".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz",
}
BLOCKED_NAME_PARTS = {".env", "credential", "credentials", "secret", "secrets", "token", "private_key"}
SECRET_PATTERNS = [
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"sk-[A-Za-z0-9]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=REPO, check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def changed_paths() -> list[Path]:
    cp = run("git", "status", "--porcelain=v1", "-z", "--", ALLOWED_ROOT)
    entries = [entry for entry in cp.stdout.split("\0") if entry]
    paths: list[Path] = []
    for entry in entries:
        raw = entry[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(Path(raw))
    return paths


def verify_paths(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for rel in paths:
        if not rel.parts or rel.parts[0] != ALLOWED_ROOT:
            errors.append(f"허용 범위 밖의 파일: {rel}")
            continue
        full = REPO / rel
        if not full.exists() or not full.is_file():
            continue
        lower_name = full.name.lower()
        if full.suffix.lower() in BLOCKED_SUFFIXES:
            errors.append(f"금지된 가중치/압축 확장자: {rel}")
        if any(part in lower_name for part in BLOCKED_NAME_PARTS):
            errors.append(f"비밀정보 가능성이 있는 파일명: {rel}")
        size = full.stat().st_size
        if size > MAX_FILE_BYTES:
            errors.append(f"95MB를 초과하는 파일: {rel} ({size} bytes)")
        if size <= 5 * 1024 * 1024:
            data = full.read_bytes()
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                errors.append(f"비밀키 패턴이 감지된 파일: {rel}")
        try:
            if full.suffix.lower() in {".json", ".ipynb"}:
                json.loads(full.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"JSON 문법 오류: {rel}: {exc}")
    return errors


def require_synced_main() -> str | None:
    branch = run("git", "branch", "--show-current").stdout.strip()
    if branch != "main":
        return f"현재 branch가 main이 아님: {branch or '(detached)'}"
    run("git", "fetch", "--quiet", "origin", "main")
    cp = run("git", "rev-list", "--left-right", "--count", "HEAD...origin/main")
    ahead, behind = (int(x) for x in cp.stdout.split())
    if ahead or behind:
        return f"로컬과 origin/main이 동기화되지 않음: ahead={ahead}, behind={behind}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="검증만 수행하고 commit/push하지 않음")
    args = parser.parse_args()

    if not (REPO / ".git").exists():
        print(f"자동 업로드 오류: Git 저장소를 찾을 수 없음: {REPO}")
        return 2

    paths = changed_paths()
    if not paths:
        return 0

    errors = verify_paths(paths)
    if errors:
        print("자동 업로드 차단:\n- " + "\n- ".join(errors))
        return 3

    sync_error = require_synced_main()
    if sync_error:
        print(f"자동 업로드 차단: {sync_error}")
        return 4

    if args.dry_run:
        print("DRY-RUN PASS: " + ", ".join(str(path) for path in paths))
        return 0

    run("git", "add", "-A", "--", ALLOWED_ROOT)
    staged = run("git", "diff", "--cached", "--name-only", "--", ALLOWED_ROOT).stdout.splitlines()
    if not staged:
        return 0

    check = run("git", "diff", "--cached", "--check", check=False)
    if check.returncode:
        run("git", "reset", "--", ALLOWED_ROOT, check=False)
        print("자동 업로드 차단: git diff --check 실패\n" + check.stdout + check.stderr)
        return 5

    kst = timezone(timedelta(hours=9))
    stamp = datetime.now(kst).strftime("%Y-%m-%d %H:%M KST")
    message = f"Auto-publish experiment results: {stamp}"
    commit = run("git", "commit", "-m", message, check=False)
    if commit.returncode:
        print("자동 업로드 오류: commit 실패\n" + commit.stdout + commit.stderr)
        return 6

    push = run("git", "push", "origin", "main", check=False)
    if push.returncode:
        print("자동 업로드 오류: push 실패\n" + push.stdout + push.stderr)
        return 7

    sha = run("git", "rev-parse", "--short=8", "HEAD").stdout.strip()
    print(f"GitHub 실험 결과 자동 업로드 완료: {sha} | {len(staged)}개 파일 | " + ", ".join(staged))
    return 0


if __name__ == "__main__":
    sys.exit(main())

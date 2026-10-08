#!/usr/bin/env python3
"""Install a committed Hadalird release without enabling its integrations."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ("HadalisSession.qml", "services", "modules", "assets", "LICENSE")
HELPERS = ("scripts/integrations", "scripts/todo", "scripts/notes")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble(source, target, sha):
    target.mkdir()
    for name in PAYLOAD + HELPERS:
        original, output = source / name, target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        if original.is_dir():
            shutil.copytree(original, output, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(original, output)
    manifest = json.loads((source / "manifest.json").read_text())
    manifest.update(sourceSha=sha, files={str(p.relative_to(target)): digest(p)
                    for p in sorted(target.rglob("*")) if p.is_file()})
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def owned_link(data_root):
    link = data_root / "current"
    if link.exists() or link.is_symlink():
        if not link.is_symlink() or link.resolve().parent != (data_root / "releases").resolve():
            raise ValueError("Preserve the existing unowned current path before installing")
    return link


def install(data_root, source=ROOT):
    source = Path(source).resolve()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=source, text=True)
    if dirty:
        raise ValueError("Commit source changes before installing an exact Hadalird revision")
    releases = data_root / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    link = owned_link(data_root)
    release = releases / sha
    if release.exists():
        manifest = json.loads((release / "manifest.json").read_text())
        if manifest.get("sourceSha") != sha:
            raise ValueError("Existing release identity does not match")
        for name, expected in manifest["files"].items():
            path = release / name
            if path.resolve().is_relative_to(release.resolve()) is False or digest(path) != expected:
                raise ValueError("Existing release was modified; preserve it before reinstalling")
    else:
        with tempfile.TemporaryDirectory(prefix=".stage-", dir=releases) as stage:
            payload = Path(stage) / "payload"
            assemble(source, payload, sha)
            os.replace(payload, release)
    temporary = data_root / (".current-" + str(os.getpid()))
    try:
        temporary.symlink_to(release.relative_to(data_root))
        os.replace(temporary, link)
    finally:
        temporary.unlink(missing_ok=True)
    return release


def uninstall(data_root):
    link = owned_link(data_root)
    if link.is_symlink():
        link.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--data-home", type=Path, default=Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")))
    args = parser.parse_args()
    data_root = (args.data_home / "hadalird").resolve()
    data_root.mkdir(parents=True, exist_ok=True)
    with (data_root / ".install.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.action == "install":
            print("Installed Hadalird:", install(data_root))
        else:
            uninstall(data_root)
            print("Disabled the package link; releases and user data are preserved")
    print("Run inir ipc hadalird refresh, or restart Hadalis, to apply the change")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))

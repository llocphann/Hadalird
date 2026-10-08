#!/usr/bin/env python3
"""Owned-link, exact-source and helper staging contracts; never uses the desktop."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

with tempfile.TemporaryDirectory(prefix="hadalird-install-") as name:
    private = Path(name)
    source = private / "source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    for args in (("init", "-b", "main"), ("add", "."),
                 ("-c", "user.name=Fixture", "-c", "user.email=fixture@invalid", "commit", "-m", "fixture")):
        subprocess.run(["git", *args], cwd=source, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = private / "data/hadalird"
    data.mkdir(parents=True)
    release = installer.install(data, source)
    assert (data / "current").resolve() == release
    before = (release / "manifest.json").read_bytes()
    assert installer.install(data, source) == release
    assert (release / "manifest.json").read_bytes() == before
    manifest = json.loads(before)
    assert all(installer.digest(release / path) == digest for path, digest in manifest["files"].items())
    installer.uninstall(data)
    assert not (data / "current").exists() and release.exists()
    foreign = private / "foreign"
    foreign.mkdir()
    (data / "current").symlink_to(foreign)
    for action in (lambda: installer.install(data, source), lambda: installer.uninstall(data)):
        try:
            action()
            raise AssertionError("unowned link accepted")
        except ValueError:
            pass
    assert foreign.exists()
    (data / "current").unlink()
    (release / "HadalisSession.qml").write_text("modified")
    try:
        installer.install(data, source)
        raise AssertionError("modified release accepted")
    except ValueError:
        pass
    (source / "README.md").write_text("uncommitted")
    try:
        installer.install(data, source)
        raise AssertionError("dirty source accepted")
    except ValueError:
        pass
    stage = private / "system"
    subprocess.run(["make", "install-helpers", "DESTDIR=" + str(stage), "LIBEXECDIR=/custom/libexec"], cwd=source, check=True, stdout=subprocess.DEVNULL)
    assert (stage / "custom/libexec/inir-thinkfan").is_file()
    assert "/custom/libexec/inir-thinkfan" in (stage / "usr/share/polkit-1/actions/org.inir.thinkfan.policy").read_text()
    assert not (stage / "etc").exists()
print("HADALIRD_INSTALL_PASS exact source, immutable release, owned link, idempotence, prefix/DESTDIR, no profiles")

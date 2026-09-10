"""Install lodsmith into the user's Blender 5.2 extension repo and enable it."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import bpy

ROOT = Path(r"C:\Users\JHH\lodsmith")
INCLUDE = (
    "blender_manifest.toml",
    "__init__.py",
    "addon",
    "recipes",
    "sets",
)


def _repos() -> None:
    prefs = bpy.context.preferences
    ext = getattr(prefs, "extensions", None)
    if ext is None:
        print("NO_EXTENSIONS_PREFS")
        return
    for repo in ext.repos:
        print(
            "REPO",
            getattr(repo, "module", None),
            getattr(repo, "name", None),
            getattr(repo, "directory", None),
            getattr(repo, "source", None),
        )


def _zip_extension(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in INCLUDE:
            path = ROOT / name
            if path.is_file():
                archive.write(path, arcname=f"lodsmith/{name}")
                continue
            for file in path.rglob("*"):
                if file.suffix in {".pyc"} or file.name == "__pycache__":
                    continue
                if "__pycache__" in file.parts:
                    continue
                archive.write(file, arcname=f"lodsmith/{file.relative_to(ROOT).as_posix()}")
    print("ZIP", dest, "bytes", dest.stat().st_size)
    return dest


def main() -> int:
    _repos()
    zip_path = _zip_extension(Path(bpy.app.tempdir) / "lodsmith.zip")
    result = bpy.ops.extensions.package_install_files(
        filepath=str(zip_path),
        enable_on_install=True,
        overwrite=True,
        repo="user_default",
    )
    print("INSTALL", result)
    bpy.ops.wm.save_userpref()
    print("ENABLED", [addon.module for addon in bpy.context.preferences.addons])
    return 0 if result == {"FINISHED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

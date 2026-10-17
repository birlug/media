#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import shutil

root = Path(__file__).resolve().parents[1]
command = shutil.which("magick") or shutil.which("convert")
if not command:
    raise SystemExit("Install ImageMagick to verify EXIF removal")
catalog = json.loads((root / "public/catalog.json").read_text())
assert catalog["files"], "Empty media catalog"
for item in catalog["files"].values():
    assert item["variants"], item["source"]
    for variant in item["variants"]:
        for kind in ("jpg", "webp"):
            file = root / "public" / variant[kind]
            assert file.is_file() and file.stat().st_size, file
            data = subprocess.check_output([command, str(file), "-format", "%w %h %[EXIF:*]", "info:"], stderr=subprocess.DEVNULL).decode().strip()
            assert data == f"{variant['width']} {variant['height']}", (file, data)
assert not (root / "public/originals").exists()
print(f"PASS: {len(catalog['files'])} images, dimensions, EXIF stripped, originals excluded")

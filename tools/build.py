#!/usr/bin/env python3
"""Publish sanitized media; originals stay private. Run from any directory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def build():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, help="Sync catalog to website; images stay in this media repo")
    parser.add_argument("--force", action="store_true", help="Rebuild after encoder or preset changes")
    args = parser.parse_args()
    command = shutil.which("magick") or shutil.which("convert")
    if not command:
        raise SystemExit("Install ImageMagick first")
    overrides = json.loads((ROOT / "metadata.json").read_text())
    scratch = ROOT / '.build'
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as temp:
        output = Path(temp)
        catalog = {"events": {}, "files": {}}
        generated = 0
        reused = 0
        for source in sorted((ROOT / "originals").rglob("*")):
            if not source.is_file() or source.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            relative = source.relative_to(ROOT / "originals").as_posix()
            options = overrides.get(relative, {})
            digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
            stem = Path("media") / source.relative_to(ROOT / "originals").parent / digest
            variants = []
            for target in (480, 960, 1600):
                # ponytail: cache keyed by original + fixed preset; --force after preset/encoder changes.
                cached = not args.force and all((ROOT / "public" / f"{stem}-{target}.{ext}").is_file() and (ROOT / "public" / f"{stem}-{target}.{ext}").stat().st_size for ext in ("webp", "jpg"))
                reused += int(cached)
                generated += int(not cached)
                for extension in ("webp", "jpg"):
                    dest = output / f"{stem}-{target}.{extension}"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if cached:
                        shutil.copy2(ROOT / "public" / dest.relative_to(output), dest)
                    else:
                        subprocess.run([command, str(source), "-auto-orient", "-strip",
                                        "-resize", f"{target}x>", "-background", "#121212",
                                        "-alpha", "remove", "-quality", "82", str(dest)], check=True)
                size = subprocess.check_output([command, str(output / f"{stem}-{target}.jpg"),
                                                "-format", "%w %h", "info:"]).decode().split()
                if any(variant["width"] == int(size[0]) for variant in variants):
                    continue  # Small originals must not yield duplicate srcset descriptors.
                variants.append({"width": int(size[0]), "height": int(size[1]),
                                 "webp": f"{stem}-{target}.webp", "jpg": f"{stem}-{target}.jpg"})
            item = {"id": digest, "source": relative, "alt": options.get("alt", ""),
                    "credit": options.get("credit", ""), "featured": options.get("featured", False),
                    "variants": variants}
            catalog["files"][relative] = item
            parts = source.relative_to(ROOT / "originals").parts
            if parts[:2] == ("events", "images"):
                event = catalog["events"].setdefault(parts[2], {"images": [], "posters": []})
                event["images"].append(item)
            elif parts[:2] == ("events", "poster"):
                event = catalog["events"].setdefault(parts[2], {"images": [], "posters": []})
                event["posters"].append(item)
        if not catalog["files"]:
            raise SystemExit("No originals found; restore private backup before rebuilding. Existing public catalog untouched.")
        unknown = set(overrides) - set(catalog["files"])
        if unknown:
            raise SystemExit(f"Unknown metadata originals: {sorted(unknown)}")
        for event in catalog["events"].values():
            event["images"].sort(key=lambda image: not image["featured"])
        (output / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
        (output / "index.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>BirLUG media</title><a href="catalog.json">BirLUG</a></html>\n')
        (output / ".nojekyll").touch()
        public = ROOT / "public"
        public.mkdir(exist_ok=True)
        # Content-hashed outputs are immutable. Keep earlier versions for old website references.
        shutil.copytree(output, public, dirs_exist_ok=True)
        if args.site:
            site = args.site.resolve()
            (site / "data").mkdir(exist_ok=True)
            shutil.copy2(public / "catalog.json", site / "data/media.json")
        print(f"Built {len(catalog['files'])} images; generated {generated}, cached {reused} widths; originals never published")

if __name__ == "__main__":
    build()

# BirLUG media

Repository origin: git@github.com:birlug/media.git. Track sanitized public outputs; keep originals private.

## Structure

- originals/: byte-verified original event photos/posters and source-font backups; ignored by Git.
- public/media/: sanitized public JPEG/WebP derivatives.
- public/catalog.json: source mapping, dimensions and variant URLs.
- metadata.json: optional owner-supplied alt/credit/featured overrides; no invented descriptions.
- tools/: preparation and publication validation.

Existing private originals were moved from ../assetsBirlug/; original website Git history was not rewritten.
Keep private original backups separately; ignore rules do not erase past public Git history.

## Prepare

ImageMagick + Python 3 required; no third-party Python packages:

```sh
python3 tools/build.py --site ../birlug.github.io
python3 tools/check.py
```

build.py strips EXIF, auto-orients, generates widths 480/960/1600 without upscaling, exports unique srcset widths.
Source hashes give immutable filenames. Cached nonempty JPEG/WebP pairs skip encoding.
Use --force after encoder/preset changes or suspected corruption. check.py validates actual image dimensions/EXIF.
Missing private originals abort rebuild without erasing existing catalog. Fresh clones can serve existing public/ without originals.

--site copies catalog ONLY; Hugo mounts this repository's public/media directory directly.
Website images do not belong in its Git index or generated static/media copy.
Never send puzzle images/binaries through this photo pipeline.

## Publish

Review photo permission/credits before new publication.
Commit public/, tools/, metadata.json, README, .gitignore and workflow; never originals/.
Workflow validates image dimensions/EXIF and publishes only public/ through GitHub Pages. No push is automatic during local preparation.
public/ is intentionally tracked here: CI publishes prepared derivatives without needing private originals. This differs from the website repository, where public/ is ignored Hugo build output.

1. Push main when publication is approved.
2. In repository Settings → Pages, select GitHub Actions as the source.
3. Check the Publish sanitized media workflow/deployment and verify its reported HTTPS URL, catalog.json and an actual image. Do not assume the default project URL; organization custom domains can affect it.
4. After verification, configure the website repository's MEDIA_BASE_URL Actions variable to that root (above media/).

Custom domain is optional, not a replacement for CI/CD. For media.birlug.ir: first verify birlug.ir ownership in the GitHub organization, then add the custom hostname in this repository's Settings → Pages, create DNS CNAME media → birlug.github.io (hostname only, no path), wait for validation/certificate issuance, and enable Enforce HTTPS. No DNS or Pages settings are changed by these files.

Current website configuration still mounts local media into generated output, even with external image URLs. Remove/override that production mount after the external host is verified; keep the local fallback for previews as needed.

Website CI expects this repository's main branch to contain prepared public/catalog.json + public/media/.
External serving is optional: MEDIA_BASE_URL must be live HTTPS site root above media/, never a guessed/placeholder URL.
Expected GitHub Pages root for this repo is https://birlug.github.io/media/ only if Pages is actually enabled and verified.

Publish media BEFORE updating website catalog references. Retain old hashed variants for existing links.
For requested takedowns, remove source + all public variants and coordinate host/cache/history removal; builds deliberately retain older immutable files.

# Contributing to deckhand-builds

Printer profiles live here. Deckhand (the tool) reads them at install
time. See [`AUTHORING.md`](AUTHORING.md) for the full schema.

## Versioning

This repo follows Deckhand's date-based CalVer:

- **Version**: `YY.M.D` (today, UTC, not zero-padded — e.g. `26.4.18`)
- **Build number**: total `git rev-list --count HEAD`
- **Tag**: `v<VERSION>-<BUILD>` (e.g. `v26.4.18-214`)

Tags are cut automatically when changes land on `main`. No manual
version bumping.

Deckhand resolves the **latest tag** of this repo by default when
fetching profiles, so every merged PR effectively rolls out to anyone
who runs the tool. Users can pin to an older tag in settings.

## Commit messages

No conventional-commits discipline required. Keep commit subjects
meaningful; each release's auto-generated notes list every commit that
landed since the previous tag.

## How releases happen

1. You push to `main`.
2. `.github/workflows/release.yml` runs.
3. It computes `VERSION=YY.M.D` + `BUILD=git rev-list --count HEAD`,
   tags the commit, and publishes a GitHub Release with auto-generated
   notes.

No installers to build here — profiles are plain files that Deckhand
fetches at install time, so the release is just a tag + notes.

## Adding a new printer profile

1. Read [`AUTHORING.md`](AUTHORING.md).
2. Create `printers/<id>/` with at minimum `profile.yaml` + `README.md`,
   starting at `status: stub`.
3. Add your profile to `registry.yaml`.
4. Open a PR.
5. On merge, the next release tag rolls your profile out.

Promote `stub` → `alpha` → `beta` → `stable` in follow-up PRs as you
validate each flow on real hardware.

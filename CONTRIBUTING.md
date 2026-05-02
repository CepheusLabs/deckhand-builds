# Contributing to deckhand-builds

Printer profiles live here. Deckhand (the tool) reads them at install
time. See [`AUTHORING.md`](AUTHORING.md) for the full schema.

## Versioning

This repo follows Deckhand's date-based CalVer:

- **Version**: `YY.M.D` (today, UTC, not zero-padded - e.g. `26.4.18`)
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

No installers to build here - profiles are plain files that Deckhand
fetches at install time, so the release is just a tag + notes.

## One-time setup

This repo carries its own pre-commit hook in `.githooks/pre-commit`.
After cloning, point git at it once:

```sh
git config core.hooksPath .githooks
```

The hook regenerates `registry.yaml` from `printers/*/profile.yaml`
whenever you commit a profile change, so the two files cannot drift.
You'll also need a sibling `deckhand` checkout (the hook runs the
`deckhand_profile_lint` tool that lives in
`<parent>/deckhand/packages/deckhand_profile_lint/`); set
`DECKHAND_LINT_DIR` if your layout differs.

## Adding a new printer profile

1. Read [`AUTHORING.md`](AUTHORING.md).
2. Create `printers/<id>/` with at minimum `profile.yaml` + `README.md`,
   starting at `status: stub`.
3. Commit the profile. The pre-commit hook adds the matching
   `registry.yaml` entry for you — `registry.yaml` is generated from
   the profile.yaml files and should never be hand-edited.
4. Open a PR.
5. On merge, the next release tag rolls your profile out.

Promote `stub` → `alpha` → `beta` → `stable` in follow-up PRs as you
validate each flow on real hardware. The hook re-syncs `registry.yaml`
on each promotion commit; if you ever need to do it manually:

```sh
dart run deckhand_profile_lint --root . --regenerate-registry
```

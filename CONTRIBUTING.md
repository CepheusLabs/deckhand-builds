# Contributing to deckhand-builds

Printer profiles live here. Deckhand (the tool) reads them at install
time. See [`AUTHORING.md`](AUTHORING.md) for the full schema.

## Commit messages

This repo uses [Conventional Commits](https://www.conventionalcommits.org)
so [release-please](https://github.com/googleapis/release-please) can
cut releases automatically.

| Type | Use for | Bumps |
|------|---------|-------|
| `feat:` | new printer profile, new wizard step kind | minor |
| `fix:` | correcting a field on an existing profile | patch |
| `profile:` | profile content changes (e.g. updating a ref, changing a service default) | patch |
| `schema:` | changes to `schema/profile.schema.json` | patch (or minor if additive, major if breaking) |
| `docs:` | AUTHORING.md / READMEs | patch |
| `chore:` | housekeeping | none |

Breaking schema changes require `schema!:` or a `BREAKING CHANGE:`
footer and bump **major**. Deckhand supports the current schema + one
previous major, so coordinate with a corresponding Deckhand release.

## How releases are cut

1. Merge PRs to `main` with conventional-commit titles.
2. Release Please maintains a **release PR** that bumps
   `.release-please-manifest.json` and appends to `CHANGELOG.md`.
3. Merging the release PR tags the repo (`vX.Y.Z`).
4. Deckhand users get the new profiles the next time they open the
   printer-picker (or on an explicit "check for updates" action).

## Adding a new printer profile

1. Read [`AUTHORING.md`](AUTHORING.md).
2. Create `printers/<id>/` with at minimum `profile.yaml` +
   `README.md`, starting at `status: stub`.
3. Add your profile to `registry.yaml`.
4. Open a PR titled `feat: add <Printer Model> profile (stub)`.
5. Promote `stub` → `alpha` → `beta` → `stable` in follow-up PRs as
   you validate each flow on real hardware.

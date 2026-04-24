# Changelog

Behavior changes in profile / step semantics that affect existing
profile authors. Schema changes land in `schema/profile.schema.json`
and the authoring guide in `AUTHORING.md`.

## Unreleased

### Changed

- **`install_marker` now routes through `write_file`.** The previous
  direct `mv` flow did not auto-snapshot an existing `deckhand.json`.
  The new flow inherits the full `write_file` pipeline: auto-backup
  to `<target>.deckhand-pre-<profile-id>-<ts>`, `.meta.json` sidecar,
  opt-out via `backup: false`. Users upgrading from an older
  Deckhand build who had a hand-edited marker (extra notes, custom
  `deckhand_schema` fields) will see that file preserved on the
  printer the first time this step re-runs.

### Added

- **`write_file.require_path`**: skips the step when the given path
  does not exist on the live printer. Lets profiles gate destructive
  writes on runtime state ("only rewrite KlipperScreen's launcher
  when KlipperScreen is actually installed").

- **`write_file.backup` / `install_marker.backup`**: default `true`,
  auto-snapshots the target before overwrite. See the
  "Backup retention" section in AUTHORING.md for the filesystem
  layout, pruning defaults, and cross-profile handling.

- **Backup metadata sidecar**. Every auto-backup writes a
  `<backup-path>.meta.json` next to the snapshot with
  `{profile_id, profile_version, step_id, created_at_ms, backup_of,
  deckhand_schema}`. Deckhand's Verify screen uses this to group
  backups by originating profile and to render "created by profile X,
  step Y, at <time>" next to each Restore button.

- **Profile-tagged backup naming**. Backups are now named
  `<target>.deckhand-pre-<profile-id>-<epoch_ms>`. Legacy
  `.deckhand-pre-<epoch_ms>` (no profile tag, no sidecar) is still
  discovered and restorable, surfaced under a distinct "Legacy
  backups" UI section.

### Changed (behavior of existing fields)

- `identification.moonraker_objects`, `identification.hostname_patterns`,
  `identification.marker_file`: unchanged semantics; just documented
  more fully.

### Schema

- `$defs/flow_spec.steps` now has a `oneOf` branch that pins
  `write_file`, `install_marker`, `script`, and `conditional`
  step-kind specific fields. Other step kinds fall through to a
  permissive generic variant (`step_generic`), so existing profiles
  using `ssh_commands`, `snapshot_paths`, etc. continue to validate.

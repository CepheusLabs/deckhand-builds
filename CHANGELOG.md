# Changelog

Behavior changes in profile / step semantics that affect existing
profile authors. Schema changes land in `schema/profile.schema.json`
and the authoring guide in `AUTHORING.md`.

## Unreleased

### Profiles

- **`sovol-sv08-max` promoted from `stub` to `alpha`.** Profile is
  now structurally complete with both `flows.stock_keep` (20 steps)
  and `flows.fresh_flash` (22 steps) declared end-to-end. Hardware,
  identity, services, MCU topology, and screen-daemon blocks all
  verified against a live audit of a stock unit. All load-bearing
  artifacts vendored from Sovol's published source at
  [Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX): stock
  configs, Sovol-original klippy/extras (`z_offset_calibration.py`,
  `probe_pressure.py`, `buffer_stepper.py`, modified
  `probe_eddy_current.py` / `ldc1612.py` / `lis2dw.py`), Katapult
  flash tooling, the pre-built H750 main-MCU firmware blob from
  Sovol's MKSDEB, and the full `zhongchuang_klipper` serial-TFT
  screen daemon source tree. Promotion to `beta` gated on validating
  flows end-to-end on real hardware.

- **Sovol SPI-XI image lineage findings.** The audit surfaced that
  the SPI-XI base image used by the Sovol SV08 Max (and the Sovol
  Zero) ships with three pre-shared SSH host keys (ed25519, RSA,
  ECDSA) all generated on a build VM named `chris-virtual-machine`
  and identical across every shipped unit. Both new profiles include
  a `regenerate_ssh_host_keys` step at the start of `stock_keep`
  that runs BEFORE any user fingerprint-trust prompt. Also surfaced:
  the `wifi_server.service` (LAN-exposed root command server with a
  trivially-escapable `/command` endpoint) is a critical-severity
  finding common to both profiles; both flows disable + mask it
  before any other LAN-side state change.

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

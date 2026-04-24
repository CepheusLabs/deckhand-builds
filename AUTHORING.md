# Authoring a Deckhand printer profile

This guide is for contributors adding or maintaining a printer profile.
End users never see this file - they use Deckhand's wizard, which reads the
profile YAML and asks the right questions.

> **Reading order:** if you're adding a new printer, read this top to bottom.
> If you're editing an existing profile, jump to the section that covers the
> field you're changing.

## Repo layout

```
deckhand-builds/
├── README.md
├── AUTHORING.md                         # this file
├── CHANGELOG.md
├── registry.yaml                        # index of available profiles
├── schema/
│   └── profile.schema.json              # JSON Schema for validation
├── shared/                              # content reusable across printers
│   ├── systemd-units/
│   └── scripts/
└── printers/
    ├── phrozen-arco/
    │   ├── profile.yaml
    │   ├── README.md
    │   ├── configs/                     # printer.cfg + friends (templated)
    │   ├── klipper-extras/              # extras modules we ship
    │   ├── firmware/                    # MCU firmware files + flash helpers
    │   ├── screen-daemon/               # our OSS screen replacement source
    │   ├── scripts/                     # install hooks, validators
    │   └── docs/                        # printer-specific docs (STOCK-INVENTORY.md, etc.)
    ├── sovol-zero/
    │   └── profile.yaml                 # stub with research_needed: true
    └── sovol-sv08-max/
        └── profile.yaml                 # stub
```

## The profile manifest - `profile.yaml`

Every printer profile has a `profile.yaml` at its root. All other files
(configs, scripts, firmware) are referenced **by relative path** from that
YAML. Deckhand never guesses - if it's not declared, it's not touched.

### Top-level skeleton

```yaml
schema_version: 1                         # bump when breaking the schema
profile_id: phrozen-arco                  # stable identifier; folder name match
profile_version: 0.1.0                    # semver for this profile
display_name: Phrozen Arco
manufacturer: Phrozen
model: Arco
status: alpha                             # stub | alpha | beta | stable | deprecated
maintainers:
  - { name: "Cepheus Labs", contact: "support@cepheuslabs.com" }
compatible_with:
  firmware_variants:                      # SKU / board revisions
    - id: default
      display_name: Arco (stock)
      notes: Only SKU observed so far.

# Hosts this profile's install flow will contact. Used for batch network
# allow-list approval at wizard start (see Deckhand ARCHITECTURE.md).
required_hosts:
  - github.com
  - raw.githubusercontent.com
  - codeload.github.com
  - redirect.armbian.com
  - archive.debian.org

# Printer identification hints for the connect screen. Tiered from
# strongest to weakest signal; see "Identification" section below.
identification:
  marker_file: deckhand.json              # written by install_marker step
  moonraker_objects: [phrozen_dev]        # stock-only fingerprint
  hostname_patterns: ['^mkspi$']          # weak fallback

hardware: { … }                           # see "Hardware declaration"
os:       { … }                           # see "OS"
ssh:      { … }                           # see "SSH"
firmware: { … }                           # see "Firmware (klippy-host)"
stack:    { … }                           # see "Stack components"
mcus:     [ … ]                           # see "MCUs"
screens:  [ … ]                           # see "Screens"
addons:   [ … ]                           # see "Addons (AMS, etc.)"
stock_os:
  detections: [ … ]                       # see "Detecting what's on the device"
  services:   [ … ]                       # see "Stock services inventory"
  files:      [ … ]                       # see "Leftover files inventory"
  paths:      [ … ]                       # see "Directory inventory"
wizard:     { … }                         # see "Wizard customization"
flows:
  stock_keep: { … }                       # see "Flow A"
  fresh_flash: { … }                      # see "Flow B"
verifiers: [ … ]                          # see "Post-install verifiers"
```

Each section is documented below with complete examples drawn from the
Arco's real configuration, so you can copy + adapt.

---

## Identification

The connect screen probes every host it finds on the LAN and tags
each card with one of: **confirmed match**, **probable match**,
**does not match**, or **unknown** (still probing). The tiers:

| Tier | Field               | Strength  | When it fires                                                                                              |
|------|---------------------|-----------|------------------------------------------------------------------------------------------------------------|
| 1    | `marker_file`       | confirmed | Deckhand installed this printer before (the `install_marker` step writes `~/printer_data/config/<file>`).  |
| 2    | `moonraker_objects` | confirmed | Stock vendor Klipper modules are registered (e.g. `phrozen_dev` on the Arco).                              |
| 3    | `hostname_patterns` | probable  | Moonraker's reported hostname matches a regex. Used when tiers 1-2 miss.                                   |

Example:

```yaml
identification:
  marker_file: deckhand.json
  moonraker_objects:
    - phrozen_dev                   # matches `phrozen_dev`, `phrozen_dev:runout`, etc.
  hostname_patterns:
    - '^mkspi$'
```

The marker file is what makes the identification durable across
`apply_files` decisions that strip vendor artefacts: add an
`install_marker` step to every flow that leaves the printer in a
"Deckhand-managed" state and you'll always recognise it on return.

---

## Hardware declaration

Basic facts the wizard uses for display + compatibility checks.

```yaml
hardware:
  architecture: aarch64                   # aarch64 | armv7l | x86_64
  sbc:
    soc: rockchip-rk3328
    board: mks-pi                         # human-friendly name shown in UI
    emmc_size_bytes: 7818182656           # optional - for flash-flow checks
  kinematics: corexy                       # corexy | cartesian | delta | scara
  build_volume_mm: { x: 330, y: 330, z: 303 }
  steppers:
    - axis: x
      driver: tmc5160
      mode: spi
    - axis: y
      driver: tmc5160
      mode: spi
    - axis: z
      driver: tmc2209
      mode: uart
      count: 2
    - axis: extruder
      driver: tmc2209
      mode: uart
  sensors:
    - { kind: thermistor, name: extruder, source: ntc }
    - { kind: thermistor, name: bed,      source: ntc }
    - { kind: thermistor, name: chamber,  source: ntc }
    - { kind: adc, name: filament, pin: "MKS_THR:PA2" }
  features:
    - motorized_probe_deploy
    - chamber_fan
    - accelerometer_on_toolhead
```

---

## OS

Declares what we know about the stock OS and what we can flash if the user
wants a fresh install.

```yaml
os:
  stock:
    distro: armbian
    version: "22.05.0-trunk"
    codename: buster
    python: "3.7"
    notes: |
      Stock OS is EOL Debian Buster with Python 3.7. Kalico and modern
      Klipper both need Python 3.9+, so a Python 3.11 build-from-source
      step is required on the stock-keep flow.
  fresh_install_options:
    - id: armbian-bookworm-cli
      display_name: Armbian Bookworm (CLI) for MKS Pi
      architecture: aarch64
      url: https://redirect.armbian.com/mkspi/Bookworm_current
      sha256: null                          # null = user must accept non-pinned hash
      size_bytes_approx: 1500000000
      recommended: true
      notes: |
        Ships Python 3.11, systemd, clean Armbian base. No Phrozen services.
  boot_mode: mbr                            # mbr | gpt
```

---

## SSH

Credentials Deckhand tries automatically. `first_matching_wins` - first
successful auth gets used. If none match, the wizard prompts.

```yaml
ssh:
  default_port: 22
  default_credentials:
    - { user: mks,  password: makerbase }
  recommended_user_after_install: mks
  fingerprint_notes: |
    First connection prompts the user to trust the host key. No pre-shared
    fingerprint; Phrozen units generate their own on first boot.
```

---

## Firmware (klippy-host)

Firmware here means the Klipper/Kalico host process that runs on the SBC,
not the MCU firmware (those are in `mcus:` below).

```yaml
firmware:
  choices:
    - id: kalico
      display_name: Kalico
      description: |
        Community-maintained Klipper fork (formerly Danger Klipper). Monthly
        rebases, adds danger_options, gcode_shell_command, trad_rack.
      repo: https://github.com/KalicoCrew/kalico
      ref: main
      install_path: "~/kalico"
      venv_path: "~/kalico-env"
      python_min: "3.9"
      recommended: true
    - id: klipper
      display_name: Klipper (modern)
      description: Upstream Klipper3D/klipper, latest master.
      repo: https://github.com/Klipper3d/klipper
      ref: master
      install_path: "~/klipper"
      venv_path: "~/klippy-env"
      python_min: "3.8"
  default_choice: kalico
  replace_stock_in_place: true              # overwrite ~/klipper on stock-keep
  snapshot_before_replace: true             # mv ~/klipper → ~/klipper.stock.<date>
  requires_python_rebuild_if:
    - condition: "os.stock.python < firmware.selected.python_min"
      action: "build-python-from-source"
```

---

## Stack components

Everything else that runs alongside klippy.

```yaml
stack:
  moonraker:
    repo: https://github.com/Arksine/moonraker
    ref: master
    install_path: "~/moonraker"
    venv_path: "~/moonraker-env"
    port: 7125
    trusted_clients:
      - 10.0.0.0/8
      - 172.16.0.0/12
      - 192.168.0.0/16
  webui:
    choices:
      - id: fluidd
        display_name: Fluidd
        release_repo: fluidd-core/fluidd
        asset_pattern: "fluidd.zip"
        install_path: "~/fluidd"
        default_port: 8808
      - id: mainsail
        display_name: Mainsail
        release_repo: mainsail-crew/mainsail
        asset_pattern: "mainsail.zip"
        install_path: "~/mainsail"
        default_port: 81
    default_choices: [fluidd]                 # array - user can pick multiple
    allow_multiple: true                      # show "Both" card
    allow_none: true                          # show "Neither - advanced" option
    force_choice: null                        # set to an id to skip the screen
  kiauh:
    repo: https://github.com/dw-0/kiauh
    ref: master
    install_path: "~/kiauh"
    default_install: true                     # offer with pre-selected Yes
    wizard:
      explainer: |
        KIAUH is the Klipper Installation And Update Helper - an interactive
        menu you run over SSH that lets you install, update, remove, and
        troubleshoot every piece of the Klipper stack. Deckhand handles your
        first-install; KIAUH handles tweaks you may want later.
      examples:
        - Install a second Klipper instance for a second toolhead
        - Swap between Klipper and Kalico without reflashing
        - Reinstall Moonraker cleanly if it breaks
        - Add a timelapse plugin
  crowsnest:
    repo: https://github.com/mainsail-crew/crowsnest
    ref: master
    install_path: "~/crowsnest"
    included: true                          # ship with the camera stack
```

---

## MCUs

Every board on the printer that runs a Klipper MCU image. The wizard uses
this to build + flash firmware.

```yaml
mcus:
  - id: main
    display_name: Main MCU (STM32F407)
    chip: stm32f407xx
    clock_hz: 168000000
    clock_ref_hz: 8000000
    flash_size: 0x80000
    application_offset: 0x8008000
    transport:
      kind: usb
      select: stm32_usb_pa11_pa12
      flash_method: dfu
      flash_device_id: "0483:df11"
    klipper_serial: "/dev/serial/by-id/usb-Klipper_stm32f407xx_*"
  - id: toolhead
    display_name: Toolhead MCU (STM32F103)
    chip: stm32f103xe
    clock_hz: 72000000
    clock_ref_hz: 8000000
    flash_size: 0x20000
    application_offset: 0x8007000
    transport:
      kind: serial
      select: stm32_serial_usart1
      baud: 250000
      flash_method: stm32flash
      flash_device_path: /dev/ttyS0
      requires_physical_access: true
      physical_access_notes: |
        Hold BOOT0 button, press RESET, release both. Then flash.
    klipper_serial: "/dev/ttyS0"
    klipper_alias: MKS_THR
```

---

## Screens

Screen daemon options the wizard offers in the screen step.

```yaml
screens:
  - id: arco_screen
    display_name: arco_screen (OSS - recommended)
    source_kind: bundled
    source_path: ./screen-daemon/           # in this profile dir
    service_name: arco-screen
    install_script: ./screen-daemon/install.sh
    supports:
      power_loss_recovery: true
      file_browser: true
      mmu_ui: partial
    status: beta
    recommended: true
  - id: voronFDM
    display_name: voronFDM (stock, closed-source ARM binary)
    source_kind: restore_from_backup        # requires user's stock eMMC image
    restore_paths:
      - "/home/mks/voronFDM"
      - "/home/mks/libwpa_stub/"
      - "/home/mks/klipper/klippy/extras/phrozen_dev/serial-screen/voronFDM"
    depends_on:
      phrozen_master: stub_or_real          # needs the UDS at /tmp/UNIX.domain
    status: stable
    notes: |
      Works well but can't be updated or audited. Bound to the specific
      TJC screen firmware shipped with the printer.
  # mksclient intentionally NOT offered - we don't understand it well enough.
```

---

## Addons (AMS, bed probes, etc.)

```yaml
addons:
  - id: chromakit
    kind: ams
    display_name: ChromaKit MMU
    units_min: 1
    units_max: 2
    slots_per_unit: 4
    protocol: serial_binary_19200
    klipper_extras:
      - source: ./klipper-extras/phrozen_dev/
        install_as: "{{firmware.install_path}}/klippy/extras/phrozen_dev"
        method: symlink
    firmware_flashing:
      tool: ./firmware/flash-chromakit.sh
      requires_transient_binaries:
        - name: phrozen_master
          source_path: "/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/phrozen_master"
          purpose: serial_relay
        - name: phrozen_slave_ota
          source_path: "/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/phrozen_slave_ota"
          purpose: flash_tool
      network_sandboxing:
        method: iptables
        block_host: "42.193.239.84"
        block_port: 7000
    firmware_blobs:                         # shipped in profile
      - path: ./firmware/chromakit/FW_Arco-AMS_H1I1_V25328.bin
        display_version: V25328
        board_variant: H1I1
```

---

## Stock OS - detections

### What is detection?

When Deckhand SSHes into a printer, it doesn't know what model it is. The
user might have followed a link straight to the app, or they hit
"auto-discover" on S20-connect and a random Moonraker instance answered.
Detection is how Deckhand figures out which profile to apply.

Each profile declares a set of small SSH probes (file exists? file
contents match a pattern? process running? command returns a specific
string?). Deckhand runs the probes from every candidate profile (or the
user-selected one, if they chose manually) and uses the results to pick a
match.

**Matching rule.** A profile matches if **all of its `required: true`
detections pass**. `required: false` detections don't gate matching but
they add confidence - used to disambiguate when multiple profiles claim a
match.

If zero profiles match, Deckhand prompts the user to pick one manually or
to pick "unsupported printer" (which disables flow A - only fresh-flash
works on unknown hardware).

If more than one profile claims a match with equal required-detection
passes, Deckhand picks the one with the most `required: false` detections
also passing, and if that's still a tie, shows the user a picker.

### Available detection kinds

| `kind` | Fields | Passes when |
|--------|--------|-------------|
| `file_exists` | `path` | File or directory exists on the remote |
| `file_absent` | `path` | File or directory does not exist |
| `file_contains` | `path`, `pattern` (regex) | File content matches the pattern |
| `process_running` | `name` (regex) | A process matching the name is in `ps` output |
| `systemd_unit_enabled` | `unit` | `systemctl is-enabled <unit>` returns enabled |
| `command_stdout_matches` | `command`, `pattern` | Running the shell command produces stdout matching the pattern |

Adding a new detection kind is a Deckhand release (not a profile change) -
profile authors can request new kinds via issues in the `deckhand` repo.

### Example

```yaml
stock_os:
  detections:
    - kind: file_exists
      path: "/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/phrozen_master"
      required: true                      # must exist for this profile to apply
    - kind: file_exists
      path: "/home/mks/phrozen_dir/phrozen_install.sh"
      required: true                      # plus this one
    - kind: file_contains
      path: "/etc/hostname"
      pattern: "mkspi"
      required: false                     # tiebreaker / confidence boost
    - kind: process_running
      name: voronFDM
      required: false
      note: "Confirms Phrozen boot path (voronFDM) vs. MKS boot path (mksclient)."
```

---

## Stock services - inventory

Each service the wizard might toggle. Drives question generation and the
review screen.

```yaml
stock_os:
  services:
    - id: frpc
      display_name: Phrozen FRP reverse tunnel
      process_pattern: "frpc"
      launched_by:
        kind: script
        path: "/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/frp/frpc_script"
      phones_home:
        - host: "42.193.239.84"
          port: 7000
      default_action: remove
      wizard:
        question: |
          Remove Phrozen's reverse tunnel?
        helper_text: |
          Always-on tunnel using a shared developer token. Possibly for a
          future mobile app, but today it's an open remote-access channel.
        options:
          - { id: keep,   label: Keep }
          - { id: remove, label: Remove (recommended) }
        recommended: remove
    - id: phrozen_master
      display_name: Phrozen HDL Zigbee gateway
      process_pattern: "phrozen_master"
      roles:
        - id: hdl_cloud_gateway
          description: Phones home to hdlcontrol.com for LED control via Zigbee.
        - id: uds_for_voronfdm
          description: Local /tmp/UNIX.domain socket voronFDM connects to.
        - id: chromakit_flash_relay
          description: Transient serial relay used by flash-chromakit.sh.
      default_action: stub_if_voronfdm_else_remove
      wizard:
        question: |
          What to do with Phrozen's HDL Zigbee gateway?
        helper_text: |
          Has three roles. We always preserve the flash relay role (via
          on-demand invocation of the binary during ChromaKit firmware
          flashing). The other two roles depend on your screen choice.
        options:
          - { id: keep,   label: Keep running (phones home, LEDs via HDL app) }
          - { id: stub,   label: Stub (satisfies voronFDM, no phone-home) }
          - { id: remove, label: Remove entirely }
        default_rules:
          - when: "screen.selected == voronFDM"
            then: stub
          - when: "screen.selected == arco_screen"
            then: remove
    - id: phrozen_ota
      display_name: Phrozen OTA stack (phrozen_slave_ota + ota_control)
      process_pattern: "phrozen_slave_ota|ota_control"
      default_action: remove
      wizard: none                          # no question - always removed
      note: |
        Not used by Kalico/Klipper/Moonraker updates. ChromaKit MCU flashing
        still works via flash-chromakit.sh which uses the binaries on demand.
    - id: makerbase_udp
      display_name: makerbase-udp (LAN HTTP/file-upload service)
      process_pattern: "udp_server"
      systemd_unit: makerbase-udp.service
      default_action: keep
      wizard:
        question: Disable the MKS LAN file-upload service?
        helper_text: |
          Listens on UDP + HTTP (wz simple httpd) with no auth. Used by MKS
          slicer / phone app for LAN discovery + gcode upload. Useful for
          some, attack surface for others.
        options:
          - { id: keep,    label: Keep (recommended if you use MKS tools) }
          - { id: disable, label: Disable (security-focused) }
    - id: makerbase_net_mods
      display_name: makerbase-net-mods (USB wifi provisioning)
      systemd_unit: makerbase-net-mods.service
      default_action: keep
      wizard:
        question: Disable the USB-stick wifi provisioning service?
        helper_text: |
          On every boot, copies wpa_supplicant.conf from a USB stick into
          /etc/. Handy for first-time setup; physical access takeover vector
          afterward.
        options:
          - { id: keep,    label: Keep }
          - { id: disable, label: Disable (recommended after wifi is set) }
    - id: makerbase_shutdown
      display_name: makerbase-shutdown (vestigial GPIO monitor)
      systemd_unit: makerbase-shutdown.service
      default_action: disable
      wizard: none
      note: |
        Monitors GPIO80 for a signal that doesn't exist on shipping hardware
        (only a rocker switch for full power-off). Leftover from a planned
        feature that wasn't completed. Disabled by default.
    - id: klipperscreen
      display_name: KlipperScreen (installed but never runs)
      systemd_unit: KlipperScreen.service
      launched_by:
        kind: script
        path: "/home/mks/KlipperScreen/scripts/KlipperScreen-start.sh"
        note: "Phrozen replaces this with a custom script that launches voronFDM."
      default_action: keep_service_rewrite_script
      wizard: none
    # ... more as discovered
```

---

## Leftover files - inventory

Per-file decisions with helper text. The wizard generates a checkbox list.

```yaml
stock_os:
  files:
    - id: rsa_priv
      display_name: HDL Zigbee gateway private key
      paths:
        - "/home/mks/hdlDat/rsa_priv.txt"
        - "/etc/hdlDat/rsa_priv.txt"
        - "/hdlFamily/rsa_priv.txt"           # if present
      default_action: delete
      wizard:
        helper_text: |
          Plaintext RSA private key used by phrozen_master to auth to HDL
          cloud. Removing it doesn't break anything we support.
        recommended: delete
    - id: elegoo_update
      display_name: Elegoo update-installer script
      paths: ["/home/mks/update.sh"]
      default_action: delete
      wizard:
        helper_text: Installs an Elegoo-branded .deb from a USB stick.
    - id: typo_files
      display_name: Typo-named leftovers
      paths:
        - "/home/mks/udo systemctl restart crowsnest"
        - "/home/mks/ystemctl status chronyd"
      default_action: delete
      wizard:
        helper_text: Accidental shell-redirect artifacts. Harmless but ugly.
    - id: root_core
      display_name: /root/core (crash dump)
      paths: ["/root/core"]
      default_action: delete
      wizard:
        helper_text: 34 MB core dump from a past mksclient crash.
    - id: phrozen_dir
      display_name: ~/phrozen_dir/
      paths: ["/home/mks/phrozen_dir/"]
      default_action: delete
      wizard:
        helper_text: Phrozen's own install scaffolding directory.
    - id: hdlDat
      display_name: HDL Zigbee state directories
      paths:
        - "/home/mks/hdlDat/"
        - "/etc/hdlDat/"
        - "/hdlFamily/"
      default_action: delete_if_zigbee_removed
      wizard:
        helper_text: Zigbee gateway state. Useless without phrozen_master.
    - id: dated_notes
      display_name: Dated .txt notes in phrozen_dev/
      paths: ["/home/mks/klipper/klippy/extras/phrozen_dev/*.txt"]
      default_action: delete
      wizard:
        helper_text: Developer notes in Chinese. Not code, not config.
    - id: cmds_old
      display_name: Old duplicate extras file
      paths: ["/home/mks/klipper/klippy/extras/phrozen_dev/cmds-240226.py"]
      default_action: delete
      wizard:
        helper_text: Pre-dates the current cmds.py. Never loaded.
```

---

## Directory inventory

Key directories the wizard cares about (replace, snapshot, or leave).

```yaml
stock_os:
  paths:
    - id: klipper_install
      path: "/home/mks/klipper"
      role: stock_klipper
      action: snapshot_and_replace
      snapshot_to: "/home/mks/klipper.stock.{{timestamp}}"
    - id: klippy_env
      path: "/home/mks/klippy-env"
      role: stock_klipper_venv
      action: snapshot_and_replace
      snapshot_to: "/home/mks/klippy-env.stock.{{timestamp}}"
    - id: printer_data
      path: "/home/mks/printer_data"
      role: config + state
      action: preserve
    - id: moonraker
      path: "/home/mks/moonraker"
      role: third-party
      action: preserve
```

---

## Wizard customization

Profiles can reorder, rename, replace, or insert any wizard step. Deckhand
ships a default step set; profiles declare an override that entirely
supersedes the default if present. Most profiles will only need small
tweaks - the default is a good starting point.

### Default step set (what Deckhand ships)

```
welcome → connect → identify → choose_path
  Flow A: firmware → screen → services → files → hardening → review → execute → done
  Flow B: choose_os → choose_disk → flash_confirm → flash → first_boot → firmware → screen → execute → done
```

### Overriding

```yaml
wizard:
  title: Phrozen Arco Setup
  steps_override:                           # full replacement when present
    flow_a:                                 # steps for stock-keep flow
      - builtin: welcome
      - builtin: connect
      - builtin: identify
      - builtin: choose_path
      - builtin: firmware
      - builtin: screen
      - builtin: services
      - builtin: files
      - builtin: hardening
      - id: chromakit_firmware              # profile-specific step
        title: Flash ChromaKit firmware?
        kind: choose_one
        question: |
          Your ChromaKit MCU firmware may be out of date. Flash the latest
          shipped in this profile?
        options:
          - { id: flash, label: Flash }
          - { id: skip,  label: Skip (keep current) }
      - builtin: review
      - builtin: execute
      - builtin: done
    flow_b:                                 # different ordering for fresh-flash
      - builtin: welcome
      - builtin: connect
      - builtin: choose_path
      - builtin: choose_os
      - builtin: choose_disk
      - builtin: flash_confirm
      - builtin: flash
      - builtin: first_boot
      - builtin: firmware
      - builtin: screen
      - id: chromakit_firmware              # same custom step, later in flow
        kind: choose_one
        # ... same as above ...
      - builtin: execute
      - builtin: done
```

### Custom step kinds

| `kind` | What it renders |
|--------|-----------------|
| `prompt` | Rich text + primary/secondary buttons (no decision to record) |
| `choose_one` | Radio group (options populate the decision) |
| `choose_many` | Checkbox list |
| `text_input` | Single text field (stored as a decision variable) |
| `confirm` | Modal warning with explicit opt-in checkboxes |
| `run_script` | Executes a profile-provided script (SSH) - for advanced flows |

The `builtin:` entries reference Deckhand-native screens; the custom `id:`
entries are defined inline in the profile. Decisions made in custom steps
are available in expressions (see "Expression DSL" below) keyed by the
step's `id`.

---

## Expression DSL

Fields like `when:` on custom wizard steps, `default_rules[].when` inside
service declarations, and flow step `kind: conditional` use a small
declarative expression DSL. Profiles never ship code - they compose
**Deckhand-registered predicates** with boolean operators.

### Grammar

```
expr   := predicate
        | expr AND expr
        | expr OR expr
        | NOT expr
        | ( expr )

predicate := <name>(<arg>, <arg>, ...)
```

Argument syntax: bare identifiers are decision-path lookups (e.g.
`firmware.selected.id`); strings are quoted; numbers and booleans are
literal.

### Registered predicates (v1)

| Predicate | Returns true when |
|-----------|-------------------|
| `equals(path, value)` | The decision at `path` equals `value` |
| `in_set(path, [values])` | The decision at `path` is in the set |
| `selected(step_id, option_id)` | The user chose `option_id` at `step_id` |
| `profile_field_equals(path, value)` | A field in the active profile matches |
| `remote_file_exists(path)` | A file exists on the printer (SSH probe) |
| `remote_service_active(unit)` | `systemctl is-active <unit>` returns active |
| `remote_process_running(pattern)` | Matching process in `ps` |
| `os_python_below(version)` | Stock OS's Python is older than `version` |
| `decision_made(path)` | A decision at `path` has been recorded (exists) |

New predicates added by Deckhand releases; profiles can't define their own.
This is the safety boundary - profiles are pure data, never execute code.

### Examples

```yaml
# Service default: stub phrozen_master if screen is voronFDM, else remove
default_rules:
  - when: selected(screen, voronFDM)
    then: stub
  - when: NOT selected(screen, voronFDM)
    then: remove
```

```yaml
# Custom wizard step that only shows on the stock-keep flow
- id: chromakit_firmware
  when: selected(choose_path, stock_keep) AND os_python_below("3.9")
  # ...
```

```yaml
# Conditional flow step
- id: python_rebuild
  kind: conditional
  when: os_python_below("3.9")
  then:
    - { kind: script, path: shared/scripts/build-python-3.11.sh }
```

### Validation

Deckhand validates every expression at profile load time. Unknown
predicates, wrong arg counts, or unresolvable paths fail with a clear
error that references the YAML line. CI in `deckhand-builds` runs the same
validator on every PR.

### Escape hatch: Dart scripts

For logic that doesn't fit cleanly into predicate composition, profiles
can ship Dart script files under the profile's `scripts/` directory and
reference them from YAML:

```yaml
default_rules:
  - when: script("scripts/advanced_screen_decision.dart")
    then: stub
```

or as a full decision function:

```yaml
services:
  - id: complex_example
    decision_script: "scripts/decide_complex.dart"
```

**Script contract:**

```dart
// scripts/decide_complex.dart
import 'package:deckhand_profile_script/api.dart';

@ProfileScript(kind: 'service_decision')
Future<ServiceAction> decide(ScriptContext ctx) async {
  final firmware = ctx.decision<String>('firmware.selected.id');
  final remote   = await ctx.ssh.fileExists('/etc/some/path');
  if (firmware == 'kalico' && remote) {
    return ServiceAction.stub;
  }
  return ServiceAction.remove;
}
```

**Sandbox guarantees.** Scripts run in a restricted Dart isolate:

- No `dart:io`, `dart:ffi`, `dart:cli` access
- No raw filesystem access
- No arbitrary network access
- Allowed APIs: `ScriptContext` (decisions read-only, SSH probes via the
  same host session, profile field lookups, logging)
- Execution timeout: 10s default; profile can override up to 60s

**Review expectation.** Because scripts execute on the user's machine
during install, they go through the same PR review process as any other
contribution. Deckhand ships a `flutter test` integration that executes
every script against fixtures in the profile's `scripts/test/` directory -
CI fails if scripts don't have tests, if scripts reach outside the sandbox
(verified by static analysis), or if tests don't pass.

**When to use scripts vs. predicates.** Prefer predicates when you can -
they're declarative, inspectable, and safe by construction. Use scripts
only when the decision logic genuinely exceeds boolean composition of
predicate calls (rare in practice). If you find yourself wanting a new
predicate for something printer-general (e.g., "is this specific MCU
attached"), file an issue against the `deckhand` repo to add a first-class
predicate rather than scripting it.

---

## SSH authentication

Deckhand's production flow uses **password auth** against the profile's
declared default credentials. Once authenticated, it caches the
password in-memory and uses it as `sudo -S` stdin (via a transient
askpass helper) so steps that escalate don't need a pty.

**Key auth works too** but with caveats:

| Path                          | Password auth (production)          | Key auth (dev convenience)     |
|-------------------------------|-------------------------------------|--------------------------------|
| Initial SSH login             | Profile credentials                 | `~/.ssh/authorized_keys` entry |
| In-session sudo               | Cached password via `sudo -S`       | User must have NOPASSWD OR the wizard prompts (which fails on no-pty) |
| State probe + restore         | Full feature set                    | `sudo`-less commands work; `sudo`-wrapped `find /root` falls through silently |

For E2E testing against real printers, either set up NOPASSWD sudo
for the test user OR ensure the test harness supplies the password
via `DECKHAND_E2E_PASSWORD`.

## Flow A - stock-keep

Declares the sequence of operations for transforming a stock install
in-place. Many fields are printer-specific, but the ordering is common.

```yaml
flows:
  stock_keep:
    enabled: true
    preconditions:
      - kind: ssh_ok
        severity: block                     # block | warn
      - kind: free_space_min
        mountpoint: "/home/mks"
        bytes: 1500000000                   # ~1.5 GB
        severity: block
      - kind: not_printing                  # moonraker safety check
        severity: warn                      # warn only - user decides to proceed
    steps:
      - id: backup_prompt
        kind: prompt
        message: |
          Before continuing, back up the whole eMMC to an image file.
          Deckhand can do this for you (dd the physical disk).
        actions:
          - { id: backup_now,  label: Back up now (recommended) }
          - { id: i_have_one,  label: I already have a backup }
          - { id: skip,        label: Skip (not recommended) }
      - id: stop_services
        kind: ssh_commands
        commands:
          - "sudo systemctl stop klipper KlipperScreen moonraker crowsnest || true"
      - id: snapshot_paths
        kind: snapshot_paths
        paths: [klipper_install, klippy_env]
      - id: python_rebuild_if_needed
        kind: conditional
        when: "firmware.selected.python_min > os.stock.python"
        then:
          - { kind: script, path: shared/scripts/build-python-3.11.sh }
      - id: install_firmware
        kind: install_firmware
      - id: install_klipper_extras
        kind: link_extras
        sources:
          - ./klipper-extras/phrozen_dev/
          - ./klipper-extras/CatchIP.py
      - id: apply_services_decisions
        kind: apply_services
      - id: apply_files_decisions
        kind: apply_files
      - id: write_boot_hook
        kind: write_file
        target: "/home/mks/KlipperScreen/scripts/KlipperScreen-start.sh"
        template: ./scripts/KlipperScreen-start.sh.tmpl
        # write_file options:
        #   sudo:   true|false        (default: auto; true for paths
        #                              outside the SSH user's $HOME)
        #   mode:   "0644" | "0755"   (octal string, optional)
        #   owner:  "root" | "mks"    (passed to `sudo install -o`)
      - id: flash_mcus
        kind: flash_mcus
        which: [main, toolhead]
      - id: start_services
        kind: ssh_commands
        commands:
          - "sudo systemctl daemon-reload"
          - "sudo systemctl enable --now klipper moonraker"
      # The marker step is what lets the connect screen recognise
      # this printer next time - even after the user strips vendor
      # artefacts or reflashes the OS. It writes a small JSON file
      # under Moonraker's config root (default: deckhand.json).
      # Profiles that pair this with `identification.marker_file:
      # deckhand.json` get a confirmed-match badge on every rescan.
      - id: install_marker
        kind: install_marker
        filename: deckhand.json        # optional; default deckhand.json
        # target_dir: ~/printer_data/config   (default; tilde-expanded)
        # extra: { notes: "any extra keys get merged into the JSON" }
        # backup: true                       (default; see backup retention below)
      - id: run_verifiers
        kind: verify
```

Behavior note (Deckhand v26.4.23+): `install_marker` now routes through
the same `write_file` pipeline, which means a prior `deckhand.json` is
auto-snapshotted as `<target>.deckhand-pre-<profile-id>-<ts>` (plus a
`.meta.json` sidecar) before overwrite. Users upgrading from older
builds who had a hand-edited `deckhand.json` (extra notes, custom
`deckhand_schema` fields) will see that file preserved on the printer
the first time this step runs.

### kind: write_file

```yaml
- id: fix_apt_sources
  kind: write_file
  target: /etc/apt/sources.list
  template: ./scripts/sources.list.bookworm-fallback.tmpl  # OR content: "..."
  sudo: true                # explicit; default infers from target path
  mode: "0644"              # octal string; optional
  owner: root               # passed to `sudo install -o`; optional
  backup: true              # default; auto-snapshot target before overwrite
  require_path: /etc/apt    # NEW: skip the step if this path doesn't
                            # exist on the live printer. Gate steps
                            # that only make sense on specific distros
                            # or vendor layouts - e.g. rewriting a
                            # KlipperScreen launcher only when
                            # KlipperScreen is actually installed.
```

- **`sudo:`** - `true` elevates the write; `false` runs as the SSH user;
  omitting it uses the heuristic "anything outside `/home/<user>/` or
  `/tmp/` needs sudo."
- **`mode:`** - passed to `install -m <mode>` when sudo, `chmod` otherwise.
  Octal string or integer both accepted (`"0644"` or `420`).
- **`owner:`** - passed to `install -o <owner>`. Silently no-op without sudo.
- **`backup:`** - when true (default) AND the target exists, Deckhand
  does `[sudo] cp -p <target> <target>.deckhand-pre-<profile-id>-<ts>`
  before the overwrite, plus writes a `<backup>.meta.json` sidecar
  with `{profile_id, profile_version, step_id, created_at_ms,
  backup_of, deckhand_schema}`. The next run's state probe finds both
  the backup and its sidecar; the Verify screen lets the user
  Preview / Restore / Delete them. See "Backup retention" below for
  filesystem layout, pruning, and cross-profile handling.
- **`require_path:`** - when set, Deckhand probes `[ -e <require_path> ]`
  on the printer before staging the write. If the path is absent, the
  step is skipped with a log line instead of failing. Use this for
  steps that only make sense when some stock artefact is present (a
  vendor install tree, a particular config directory).

### Backup retention

Every `write_file` that actually overwrites an existing target leaves
two siblings behind:

```
/etc/apt/sources.list                                      # post-write
/etc/apt/sources.list.deckhand-pre-<profile-id>-<ts>       # byte-exact snapshot
/etc/apt/sources.list.deckhand-pre-<profile-id>-<ts>.meta.json
```

- `<profile-id>` is the profile that was driving the write.
- `<ts>` is `DateTime.now().millisecondsSinceEpoch` UTC.
- The sidecar is small (~200 bytes) and lets the Verify screen render
  "created by profile X, step Y, at 2026-04-23 00:30" next to each
  Restore button.

Legacy backups from Deckhand builds before the sidecar system exist at
`<target>.deckhand-pre-<ts>` (no profile tag, no sidecar). Deckhand
still discovers and restores those, but the Verify screen groups them
under a "Legacy backups without profile metadata" section and warns
the user to preview before restoring - content could belong to any
profile previously run against the printer.

Backups are never pruned automatically. The Verify screen's "Prune
backups older than N days" control (default 30 days) does the sweep
on demand. The `Keep the newest snapshot per target` option spares
one backup per `<target>` even if it's old enough to prune, so a
catastrophic mistake always has at least one rollback path.

Backup discovery uses `find /etc /home /opt /var /srv /root -maxdepth 8`
with the `/root` leg wrapped in `sudo -n` so root-owned backups are
visible to the non-root SSH user. Paths outside those roots (unusual
for printer images) are NOT discovered.

### kind: script

Scripts are uploaded to `/tmp/deckhand-<basename>` and executed via
`bash` (overridable with `interpreter:`). Options:

```yaml
- kind: script
  path: shared/scripts/build-python-3.11.sh
  interpreter: bash            # default
  args: ["--prefix", "/usr/local"]  # optional, shell-quoted for you
  timeout_seconds: 1800        # default 600
  ignore_errors: false         # step fails on non-zero exit by default
  sudo: false                  # default; set true to run the whole
                               # script as root via `sudo -E`
  askpass: true                # default; stages a transient askpass
                               # helper + PATH-shim sudo wrapper so
                               # the script's *internal* `sudo X`
                               # calls authenticate over SSH without
                               # a pty. Set false for scripts you
                               # want to prove never elevate.
```

**How elevation is handled (no-pty SSH):** Deckhand SSH sessions
don't allocate a pty, so plain `sudo X` inside a script hangs
waiting for a password. To make scripts written for an interactive
shell Just Work, Deckhand's default is to stage two tiny files on
the printer before each script step:

- `/tmp/deckhand-askpass-<ts>` (0700): a shell script that prints
  the cached SSH password on stdout. sudo reads it via the standard
  `SUDO_ASKPASS` contract.
- `/tmp/deckhand-bin-<ts>/sudo` (0755): a PATH-shim that forwards
  to `/usr/bin/sudo -A "$@"`. With that directory at the front of
  the script's PATH, every `sudo cmd` inside the script becomes
  `sudo -A cmd`, which consults the askpass helper.

Both files are wiped in a `finally` block after the script returns
(success or fail). The password is only on disk for the lifetime of
the step; SSH already holds the same password in memory, so there's
no privilege-level leak.

Use `sudo: true` when you want the whole script to run as root from
line 1. This wraps the invocation in `sudo -E` (with the same
password cache). Most scripts don't need this; they can rely on the
askpass helper for the handful of internal commands that need root.

Use `askpass: false` as a belt-and-suspenders declaration that a
given script must not elevate. Deckhand won't stage the helper, and
any `sudo` inside the script will fail loudly with the usual no-pty
error - making the intent auditable.

---

## Flow B - fresh-flash

```yaml
flows:
  fresh_flash:
    enabled: true
    steps:
      - id: choose_os_image
        kind: choose_one
        options_from: os.fresh_install_options
      - id: choose_target_disk
        kind: disk_picker
        filter:
          bus: [usb]
          removable: true
          size_near_bytes: "{{ hardware.sbc.emmc_size_bytes }}"
      - id: download_os
        kind: os_download
      - id: flash_disk
        kind: flash_disk
        verify_after_write: true
      - id: flash_done_prompt
        kind: prompt
        message: |
          Flash complete. Put the eMMC back in the printer and power on.
          When you can SSH to the printer, click Continue.
      - id: wait_for_ssh
        kind: wait_for_ssh
        timeout_seconds: 600
      - id: first_boot_setup
        kind: ssh_commands
        commands:
          - "sudo apt-get update"
          - "sudo apt-get install -y git python3-venv build-essential"
      - id: install_firmware
        kind: install_firmware
      - id: install_moonraker_and_webui
        kind: install_stack
      - id: install_klipper_extras
        kind: link_extras
      - id: install_screen
        kind: install_screen
      - id: flash_mcus
        kind: flash_mcus
      - id: run_verifiers
        kind: verify
```

---

## Post-install verifiers

Declarative checks Deckhand runs at the end of a flow to prove the install
worked. If any fail, the wizard shows the user a troubleshooting screen.

```yaml
verifiers:
  - id: klipper_service_active
    kind: ssh_command
    command: "systemctl is-active klipper"
    expect_stdout_contains: active
  - id: moonraker_reports_klipper
    kind: http_get
    url: "http://{{host}}:7125/printer/info"
    expect_json_path: "$.result.state"
    expect_value: ready
  - id: chromakit_connect
    kind: moonraker_gcode
    command: P28
    expect_exit: ok
  - id: no_phonehome_processes
    kind: ssh_command
    command: "ps aux | grep -E 'phrozen_master|frpc|slave_ota|ota_control' | grep -v grep | wc -l"
    expect_stdout_equals: "0"
```

---

## Templating

String fields can contain `{{…}}` template expressions. Available
variables:

| Var | Meaning |
|-----|---------|
| `host`, `port`, `user` | current SSH session target |
| `firmware.selected.*` | the firmware option the user chose |
| `screen.selected.*` | chosen screen option |
| `os.stock.*` | stock OS fields |
| `hardware.*` | hardware block |
| `timestamp` | UTC ISO8601 at install time, dashes-only |
| `profile.*` | any profile field, dot-path |

Template engine is Mustache-style (no logic, just substitution).

---

## Schema versioning

- `schema_version: 1` - initial.
- Breaking changes bump major. Deckhand supports current + one previous.
- Add new optional fields freely at the same major.

---

## Profile status lifecycle

```
stub  →  alpha  →  beta  →  stable
                     │
                     └────→  deprecated
```

| `status` | What it means | Visible in wizard? |
|----------|---------------|--------------------|
| `stub` | Exists as a placeholder. Core fields missing. Not installable. | Hidden by default. Settings toggle "show stubs" for contributors. |
| `alpha` | Installable but untested or known-rough. Flash flows may be broken. | Shown with an "alpha" badge and a warning pre-install. |
| `beta` | Installable and validated on at least one real unit. Minor issues possible. | Shown with a "beta" badge. |
| `stable` | Validated across the expected hardware variants. | Default - no badge. |
| `deprecated` | Profile is maintained only for users who already installed it. No new installs encouraged. | Shown dimmed with a "deprecated" note and a link to the recommended alternative. |

## Contributing a new printer

1. Create `printers/<printer-id>/` with at minimum `profile.yaml` + `README.md`.
2. Start with `status: stub`. Fill in what you know (name, manufacturer,
   hardware facts, upstream firmware URLs).
3. Add the profile to `registry.yaml`.
4. Open a PR. CI validates `profile.yaml` against `schema/profile.schema.json`.
5. Promote to `alpha` → `beta` → `stable` as you validate flows on real
   hardware. Each promotion is a separate PR documenting what you verified.

A `stub` profile that says "I know this printer exists but I haven't done
the work yet" is valid and valuable - it tells contributors where to start.

# Sovol Zero profile (stub)

Placeholder profile — not installable yet.

## What's needed to promote this to `alpha`

Someone with a Sovol Zero needs to gather:

1. **Hardware facts** — SBC model (SoC, board), architecture, kinematics,
   build volume, stepper drivers, sensors.
2. **Stock OS** — distro and version, default SSH user/password, python
   version shipped. Flash-a-fresh-image instructions if applicable.
3. **MCU details** — chip family, clock, flash size + offset, transport
   (USB DFU? serial?), klipper serial path (`/dev/serial/by-id/...`).
4. **Screen** — does it have a touchscreen? If so, what protocol
   (Nextion? QT? custom?). Does Sovol run a closed-source daemon?
5. **Stock services and phone-home** — full systemd inventory, any vendor
   services that phone home, any files they drop on disk.
6. **Detection rules** — a few stable file-existence or process checks
   that reliably identify a stock Sovol Zero on SSH.

See `../phrozen-arco/` for a fully-populated example profile.

## Contributing

1. Fill in `profile.yaml` incrementally. Even partial fills are useful
   for discovery.
2. Open a PR against this repo. Title prefix: `sovol-zero:`.
3. When the stock-keep and fresh-flash flows work end-to-end, bump
   `status` to `alpha` and send a follow-up PR.

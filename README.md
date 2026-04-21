# Deckhand Builds

Printer profiles consumed by [Deckhand][deckhand] - the OSS Klipper setup
tool from [Cepheus Labs][cepheus]. Each profile defines everything Deckhand
needs to flash, install, and configure a specific printer model.

> **Status: design phase.** No stable profiles yet - schema is still
> stabilizing. Contributions welcome once we tag `v0.1.0`.

## Start here

- [`AUTHORING.md`](AUTHORING.md) - the full `profile.yaml` schema and
  contributor guide. **Read this first if you're adding or editing a
  printer.**
- `registry.yaml` - index of available profiles (coming with v0.1.0).
- `printers/<id>/` - one directory per printer. Each has its own
  `profile.yaml`, configs, scripts, firmware tools, and docs.

## What lives here vs. what gets fetched

This repo contains **only** the small stuff: YAML manifests, config
templates, ChromaKit firmware blobs, our own screen daemon source,
printer-specific scripts, docs. Total size stays small (tens of MB).

Deckhand fetches everything else from upstream at install time:

- OS images → Armbian
- Klipper / Kalico → their respective GitHub repos
- Moonraker → Arksine/moonraker
- Fluidd / Mainsail → their release assets

See the [fetch strategy section][fetch] in Deckhand's architecture doc.

## Contributing a new printer

1. Read [`AUTHORING.md`](AUTHORING.md).
2. Create `printers/<printer-id>/` starting with `status: stub`.
3. Fill in what you know. It's fine to ship a stub while you flesh it out.
4. Open a PR. CI validates against the profile schema.
5. Promote `stub` → `alpha` → `beta` → `stable` as you validate each flow
   against real hardware.

## License

[AGPL-3.0](LICENSE).

[deckhand]: https://github.com/CepheusLabs/deckhand
[cepheus]: https://github.com/CepheusLabs
[fetch]: https://github.com/CepheusLabs/deckhand/blob/main/docs/ARCHITECTURE.md#profile-fetch-strategy

# Changelog

## 1.0.0 (2026-04-17)


### Bug fixes

* **profile:** drop kiauh? pseudo-syntax, normalize YAML whitespace ([b814c3b](https://github.com/CepheusLabs/deckhand-builds/commit/b814c3bf1c991812c0da8fc785c888f3fba408c5))


### Schema changes

* add profile.schema.json for CI validation ([859b51e](https://github.com/CepheusLabs/deckhand-builds/commit/859b51e74aac1f03302e777328bd23a7b54dd12b))


### Documentation

* profile.yaml schema and authoring guide ([161449e](https://github.com/CepheusLabs/deckhand-builds/commit/161449e5bb304cdb4a1e0f8c461aa2d84e5509da))


### CI

* automate releases via release-please ([68716e1](https://github.com/CepheusLabs/deckhand-builds/commit/68716e1ed8567f5fd73516359b5e62c799335453))
* **release-please:** add workflow_dispatch trigger for manual kickoff ([d2d3318](https://github.com/CepheusLabs/deckhand-builds/commit/d2d3318d320b3ced1e58482d13ded8252ac44ef1))
* **release-please:** auto-merge the release PR once CI passes ([9b64a53](https://github.com/CepheusLabs/deckhand-builds/commit/9b64a538f2f80df66a7fabd8c18f79e6477d9c5e))
* validate profile structure and YAML syntax ([cdfe277](https://github.com/CepheusLabs/deckhand-builds/commit/cdfe277327524f90fe1b6c617dfda64be3b0644b))

## Changelog

Managed by [release-please](https://github.com/googleapis/release-please).

Deckhand fetches the **latest semver tag** of this repo by default when
loading profiles, so every merged release PR effectively rolls out to
anyone who runs the tool. Users can pin to an older tag in settings.

<!-- release-please-started-tracking -->

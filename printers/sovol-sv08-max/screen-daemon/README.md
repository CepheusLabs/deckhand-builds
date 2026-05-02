# zhongchuang_klipper — SV08 Max serial-TFT screen daemon

Open-source C++17 daemon that drives the Sovol SV08 Max's serial TFT
touchscreen. Connects to Moonraker via WebSocket on `localhost:7125`
and speaks a Nextion-class serial protocol to the panel over
`/dev/ttyS3`.

This directory is vendored verbatim from Sovol's published source at
[Sovol3d/SV08MAX](https://github.com/Sovol3d/SV08MAX/tree/main/home/sovol/zhongchuang)
(`home/sovol/zhongchuang/`), minus the `build/` artifacts and the
pre-built `wpa_test`/`wpa_wifi` binaries. Sovol's internal git origin
is `http://192.168.1.233/root/zhongchuang.git` (LAN-only, decorative).

## Lineage

Makerbase mksclient derivative. The bulk of the source files
(`MoonrakerAPI.cpp`, `KlippyGcodes.cpp`, `KlippyRest.cpp`,
`MakerbasePanel.cpp`, `MakerbaseShell.cpp`, `MakerbaseSerial.cpp`,
`MakerbaseParseIni.cpp`, `process_messages.cpp`, `refresh_ui.cpp`,
`ui.cpp`, `event.cpp`, `file_list.cpp`, `wifi_list.cpp`, `mks_*.cpp`)
trace back to Makerbase's open-source MKS-Pi screen daemon — the
same lineage as the closed binary on the Phrozen Arco
(`makerbase-client.service` running `mksclient`) but Sovol kept the
distribution open and added a printer-specific layer on top.

Sovol's additions:

- `src/sovol_http.cpp` — HTTP client that wraps Comgrow OTA progress
  notifications and surfaces them on the TFT panel during `_OTA`
  runs. Note: on the SV08 Max the OTA daemon isn't started at boot
  (Sovol commented it out in `/boot/scripts/btt_init.sh`), so this
  code path is effectively dormant.
- The CMake build system + `MKSDEB/` debian-package staging scaffold.

## Build

```bash
sudo apt-get install -y \
    build-essential cmake \
    libboost-all-dev libcurl4-openssl-dev libwpa-client-dev \
    nodejs   # NodeSource Node 22 is needed by wpa.mk
mkdir -p build
cd build
cmake ..
make -j"$(nproc)"
```

Produces `build/zhongchuang_klipper` (~8.6 MB ELF aarch64). Sovol's
`builddeb.sh` then packages it into a debian package (renamed
`KLP_SOC_MKS_SKIPR-08max_<date>.deb`) for distribution. We don't go
through the deb step on Deckhand installs — we just copy the binary
+ `start.sh` + the systemd unit into place directly.

## Files in this directory

| Path | Purpose |
|------|---------|
| `CMakeLists.txt` | Build system entry point. `add_executable(zhongchuang_klipper main.cpp)`, links pthread + boost_system + wpa_client + curl. |
| `main.cpp` | Daemon entry point. |
| `src/` | 26 .cpp files implementing the Moonraker bridge, panel UI, serial I/O, file browser, gcode dispatch, OTA progress UI, etc. |
| `include/` | Headers. |
| `lib/` | Pre-built static libraries the build links against (e.g. libwpa_client.so). |
| `service/makerbase-client.service` | Systemd unit. User=root, libSegFault preloaded, unlimited core dumps, restart on failure. |
| `start.sh` | Daemon launcher. Sets up GPIO 79 for vibration feedback, configures an LED state via the `io` register-poke binary, then `exec`s `zhongchuang_klipper localhost`. |
| `script.py` | Helper invoked by start.sh. |
| `builddeb.sh` | Sovol's deb-packaging script. Not invoked by Deckhand; preserved for reference. |
| `gene5.py` | Sovol-internal codegen helper. Not invoked at runtime. |
| `wpa.mk`, `wpa_test.c`, `wpa_wifi.c` | Companion utilities for WPA-CLI interaction (used by the WiFi setup screens on the panel). The pre-built binaries are not vendored — they're rebuilt on install. |

## Closed-source pieces

The TFT panel firmware itself (`众创klipper.tft.bak` on the printer,
9.7 MB Nextion-format blob) is **closed-source ZhongChuang vendor
firmware**, separate from the open-source daemon. Deckhand does not
redistribute it — users keep whatever ships on their panel.

The `io` binary in Sovol's `build/` (an Allwinner H616
register-poker from userspace, used by `start.sh` to configure an
LED) is published in the source repo as a pre-built ELF without
matching source. The daemon works without it — only the LED
indicator is affected — so we ignore it on Deckhand installs.

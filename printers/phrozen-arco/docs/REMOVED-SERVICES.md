# Removed Services

Services and binaries removed from the stock Phrozen firmware. None of these
are required for printing or AMS operation.

## phrozen_master (HDL Zigbee Gateway)

- **Binary**: `/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/phrozen_master`
- **Size**: 4.6MB ARM binary
- **What it does**: HDL Buspro/ALink Zigbee gateway daemon. Manages enclosure
  LED control via Zigbee and connects to HDL's cloud infrastructure.
- **Connects to**:
  - `global.hdlcontrol.com` (HDL Cloud API)
  - `china-gateway.hdlcontrol.com` (China region gateway)
  - MQTT broker (credentials fetched dynamically from HDL)
  - `42.193.239.84:8080` (HTTPS)
- **Data sent**: Device MAC address, gateway ID, Zigbee device topology,
  firmware versions, telemetry
- **Why removed**: Phones home to Chinese cloud servers. Not needed for
  printing. Enclosure LEDs are cosmetic.

## frpc (FRP Tunnel)

- **Binary**: `/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/frp/frpc`
- **Config**: `/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/frp/frpc.ini`
- **Size**: 9.2MB ARM binary
- **What it does**: Fast Reverse Proxy client. Tunnels local services through
  Phrozen's cloud server for remote access.
- **Tunnels**:
  - SSH (local 22 -> remote 34978)
  - MQTT (local 1883 -> remote 8200)
  - Fluidd (local 8808 -> remote 21589)
- **Server**: `42.193.239.84:7000` with token `lancaigang` (developer's name)
- **Why removed**: Creates a remote access backdoor. Anyone with the server
  address and token can reach your printer's SSH and web UI.

## phrozen_slave_ota (OTA Updater)

- **Binary**: `/home/mks/klipper/klippy/extras/phrozen_dev/frp-oms/phrozen_slave_ota`
- **Size**: 882KB ARM binary
- **What it does**: Receives firmware updates pushed from Phrozen's cloud
  and applies them to the AMS boards and Klipper extras module.
- **Why removed**: Uncontrolled updates. Could overwrite your config or
  introduce new phone-home services.

## ota_control (OTA Controller)

- **Binary**: `/home/mks/klipper/klippy/extras/phrozen_dev/serial-screen/ota_control`
- **Size**: 4.5MB ARM binary
- **What it does**: Controls OTA update flow between the serial screen, AMS
  boards, and the main SBC.
- **Why removed**: Part of the OTA update system. Not needed when managing
  firmware manually.

## hdlDat/ (Zigbee Gateway Data)

- **Path**: `/home/mks/hdlDat/`
- **Contents**:
  - `rsa_priv.txt` - **Plaintext RSA private key** (security risk)
  - `NVImage.bin` - Zigbee coordinator firmware (148KB)
  - `ZbGwId.dat` - Gateway ID (device MAC `40d95a0388a2`)
  - `ZbCoordinatorDebug.log` - 80KB debug log
  - Various `*.dat` files for Zigbee device lists, security zones, bindings
- **Why removed**: All data for the HDL Zigbee gateway. Without `phrozen_master`,
  these files are inert but the private key is a security risk.

## How to Verify Removal

After deployment, confirm no phone-home services are running:

```bash
# Check for running processes
ps aux | grep -iE 'phrozen_master|frpc|slave_ota|ota_control' | grep -v grep

# Check for outbound connections
ss -tnp | grep -E '42\.193\.239\.84|hdlcontrol\.com'

# Check systemd services
systemctl status frpc.service 2>/dev/null
```

All of the above should return empty/not found.

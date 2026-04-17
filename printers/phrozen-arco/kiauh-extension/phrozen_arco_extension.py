import shutil
import subprocess
from pathlib import Path
from typing import Dict

from core.logger import DialogType, Logger
from extensions.base_extension import BaseExtension
from extensions.phrozen_arco import (
    KALICO_DIR,
    MOONRAKER_DIR,
    PHROZEN_ARCO_DIR,
    PHROZEN_ARCO_REPO,
    PRINTER_DATA,
)
from utils.fs_utils import run_remove_routines
from utils.input_utils import get_confirm
from utils.sys_utils import get_ipv4_addr


class PhrozenArcoExtension(BaseExtension):

    def install_extension(self, **kwargs) -> None:
        Logger.print_status("Installing Phrozen Arco overlay...")

        # Check Kalico is installed
        if not KALICO_DIR.exists():
            Logger.print_dialog(
                DialogType.ERROR,
                ["Kalico is not installed. Install Kalico first via KIAUH."],
            )
            return

        # Clone or update our repo
        if PHROZEN_ARCO_DIR.exists():
            Logger.print_status("Updating phrozen-arco-kalico repo...")
            subprocess.run(
                ["git", "pull"],
                cwd=PHROZEN_ARCO_DIR,
                check=True,
            )
        else:
            Logger.print_status("Cloning phrozen-arco-kalico repo...")
            subprocess.run(
                ["git", "clone", PHROZEN_ARCO_REPO, str(PHROZEN_ARCO_DIR)],
                check=True,
            )

        # Install ChromaKit extras module
        self._install_extras()

        # Install configs
        self._install_configs()

        # Install ChromaKit proxy (Moonraker component)
        self._install_proxy()

        # Install voronFDM
        self._install_voronfdm()

        # WiFi fix
        self._fix_wifi()

        # Install system deps
        self._install_deps()

        # PolKit rules
        self._install_polkit()

        # Flash MCUs
        if get_confirm("Flash MCU firmware? (required for first install)"):
            self._flash_mcus()

        Logger.print_dialog(
            DialogType.SUCCESS,
            [
                "Phrozen Arco overlay installed!",
                f"Fluidd: http://{get_ipv4_addr()}",
                "",
                "Restart Klipper to apply changes.",
            ],
        )

    def update_extension(self, **kwargs) -> None:
        Logger.print_status("Updating Phrozen Arco overlay...")

        if not PHROZEN_ARCO_DIR.exists():
            Logger.print_dialog(
                DialogType.ERROR,
                ["phrozen-arco-kalico not found. Run install first."],
            )
            return

        subprocess.run(
            ["git", "pull"],
            cwd=PHROZEN_ARCO_DIR,
            check=True,
        )

        self._install_extras()
        self._install_configs()

        Logger.print_dialog(
            DialogType.SUCCESS,
            ["Phrozen Arco overlay updated. Restart Klipper to apply."],
        )

    def remove_extension(self, **kwargs) -> None:
        Logger.print_status("Removing Phrozen Arco overlay...")

        # Remove extras from Kalico
        extras_dst = KALICO_DIR / "klippy" / "extras" / "phrozen_dev"
        catchip_dst = KALICO_DIR / "klippy" / "extras" / "CatchIP.py"
        if extras_dst.exists():
            shutil.rmtree(extras_dst)
        if catchip_dst.exists():
            catchip_dst.unlink()

        # Remove ChromaKit proxy from Moonraker
        proxy_dst = MOONRAKER_DIR / "moonraker" / "components" / "chromakit_proxy.py"
        if proxy_dst.exists():
            proxy_dst.unlink()

        # Remove voronFDM and its service
        subprocess.run(["sudo", "systemctl", "stop", "voronfdm"], check=False)
        subprocess.run(["sudo", "systemctl", "disable", "voronfdm"], check=False)
        subprocess.run(
            ["sudo", "rm", "-f", "/etc/systemd/system/voronfdm.service"],
            check=False,
        )
        voronfdm = Path.home() / "voronFDM"
        if voronfdm.exists():
            voronfdm.unlink()

        # Remove repo
        if PHROZEN_ARCO_DIR.exists():
            run_remove_routines(str(PHROZEN_ARCO_DIR))

        Logger.print_dialog(
            DialogType.SUCCESS,
            [
                "Phrozen Arco overlay removed.",
                "Printer configs in ~/printer_data/config/ were kept.",
                "You may need to remove [phrozen_dev] from printer.cfg.",
            ],
        )

    def _install_extras(self) -> None:
        """Copy ChromaKit extras module into Kalico."""
        Logger.print_status("Installing ChromaKit (MMU) module...")

        src = PHROZEN_ARCO_DIR / "klipper-extras" / "phrozen_dev"
        dst = KALICO_DIR / "klippy" / "extras" / "phrozen_dev"

        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

        # CatchIP helper
        catchip_src = PHROZEN_ARCO_DIR / "klipper-extras" / "CatchIP.py"
        catchip_dst = KALICO_DIR / "klippy" / "extras" / "CatchIP.py"
        shutil.copy2(catchip_src, catchip_dst)

    def _install_proxy(self) -> None:
        """Install ChromaKit proxy as a Moonraker component."""
        Logger.print_status("Installing ChromaKit proxy...")

        src = PHROZEN_ARCO_DIR / "moonraker-component" / "chromakit_proxy.py"
        dst = MOONRAKER_DIR / "moonraker" / "components" / "chromakit_proxy.py"
        shutil.copy2(src, dst)

        # Add to moonraker.conf if not present
        moonraker_conf = PRINTER_DATA / "config" / "moonraker.conf"
        if moonraker_conf.exists():
            content = moonraker_conf.read_text()
            if "[chromakit_proxy]" not in content:
                moonraker_conf.write_text(content + "\n[chromakit_proxy]\n")

    def _install_configs(self) -> None:
        """Copy printer configs to printer_data."""
        Logger.print_status("Installing printer configs...")

        config_dir = PRINTER_DATA / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_files = [
            "printer.cfg",
            "printer_MCU.cfg",
            "printer_gcode_macro.cfg",
            "moonraker.conf",
            "fluidd.cfg",
        ]

        for f in config_files:
            src = PHROZEN_ARCO_DIR / "config" / f
            dst = config_dir / f
            if src.exists():
                # Don't overwrite printer.cfg if it exists (has SAVE_CONFIG data)
                if f == "printer.cfg" and dst.exists():
                    Logger.print_status(
                        f"  Skipping {f} (already exists, has SAVE_CONFIG data)"
                    )
                    continue
                shutil.copy2(src, dst)

        # Crowsnest config with auto camera detection
        cam_dev = "/dev/video0"
        try:
            result = subprocess.run(
                ["v4l2-ctl", "--list-devices"],
                capture_output=True,
                text=True,
            )
            for i, line in enumerate(result.stdout.split("\n")):
                if "USB" in line and "Camera" in line:
                    next_line = result.stdout.split("\n")[i + 1].strip()
                    if next_line.startswith("/dev/video"):
                        cam_dev = next_line
                        break
        except Exception:
            pass

        crowsnest_conf = config_dir / "crowsnest.conf"
        crowsnest_conf.write_text(
            f"""[crowsnest]
log_path: ~/printer_data/logs/crowsnest.log
log_level: verbose
delete_log: false
no_proxy: false

[cam 1]
mode: ustreamer
port: 8080
device: {cam_dev}
resolution: 640x480
max_fps: 15
"""
        )

    def _install_voronfdm(self) -> None:
        """Install voronFDM serial screen daemon with systemd service."""
        src = PHROZEN_ARCO_DIR / "bin" / "voronFDM"
        if not src.exists():
            return

        Logger.print_status("Installing voronFDM...")
        dst = Path.home() / "voronFDM"
        shutil.copy2(src, dst)
        dst.chmod(0o755)

        # Create systemd service
        service = f"""[Unit]
Description=voronFDM Serial Screen Daemon
After=moonraker.service
Wants=moonraker.service

[Service]
Type=simple
User={Path.home().name}
ExecStart={dst}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        subprocess.run(
            ["sudo", "sh", "-c",
             f"echo '{service}' > /etc/systemd/system/voronfdm.service"],
            check=False,
        )
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=False)
        subprocess.run(["sudo", "systemctl", "enable", "voronfdm"], check=False)

    def _fix_wifi(self) -> None:
        """Apply MKS Pi WiFi fix."""
        Logger.print_status("Configuring WiFi...")

        # WiFi firmware
        fw_src = PHROZEN_ARCO_DIR / "firmware" / "os" / "wifi_efuse_8189e.map"
        if fw_src.exists():
            subprocess.run(
                ["sudo", "mkdir", "-p", "/lib/firmware/rkwifi"],
                check=False,
            )
            subprocess.run(
                ["sudo", "cp", str(fw_src), "/lib/firmware/rkwifi/"],
                check=False,
            )

        # Old DTB with WiFi support
        old_dtb = PHROZEN_ARCO_DIR / "firmware" / "os" / "old_mkspi.dtb"
        new_dtb = Path("/boot/dtb/rockchip/rk3328-mkspi.dtb")
        if old_dtb.exists() and new_dtb.exists():
            subprocess.run(
                ["sudo", "cp", str(new_dtb), str(new_dtb) + ".backup"],
                check=False,
            )
            subprocess.run(
                ["sudo", "cp", str(old_dtb), str(new_dtb)],
                check=False,
            )
            # Enable WiFi SDIO in DTB
            for node in ["/dwmmc@ff5f0000", "/mmc@ff5f0000"]:
                subprocess.run(
                    ["sudo", "fdtput", "-t", "s", str(new_dtb), node, "status", "okay"],
                    check=False,
                    capture_output=True,
                )

        # Auto-load WiFi module
        subprocess.run(
            ["sudo", "sh", "-c", "echo 8189es > /etc/modules-load.d/wifi.conf"],
            check=False,
        )

    def _install_deps(self) -> None:
        """Install system dependencies."""
        Logger.print_status("Installing system dependencies...")
        subprocess.run(
            [
                "sudo", "apt-get", "install", "-y", "-qq",
                "libsodium23", "stm32flash", "firmware-realtek",
            ],
            check=False,
        )

    def _install_polkit(self) -> None:
        """Install PolKit rules for Moonraker."""
        rules = """polkit.addRule(function(action, subject) {
    if ((action.id == "org.freedesktop.systemd1.manage-units" ||
         action.id == "org.freedesktop.login1.power-off" ||
         action.id == "org.freedesktop.login1.power-off-multiple-sessions" ||
         action.id == "org.freedesktop.login1.reboot" ||
         action.id == "org.freedesktop.login1.reboot-multiple-sessions") &&
        subject.user == "mks") {
        return polkit.Result.YES;
    }
});"""
        subprocess.run(
            ["sudo", "sh", "-c",
             f"echo '{rules}' > /etc/polkit-1/rules.d/moonraker.rules"],
            check=False,
        )

    def _flash_mcus(self) -> None:
        """Flash both MCUs with Kalico firmware."""
        Logger.print_status("Building and flashing MCU firmware...")

        kalico = str(KALICO_DIR)

        # Main MCU (STM32F407)
        Logger.print_status("Building main MCU firmware (STM32F407)...")
        config = (
            "CONFIG_MACH_STM32=y\n"
            'CONFIG_BOARD_DIRECTORY="stm32"\n'
            'CONFIG_MCU="stm32f407xx"\n'
            "CONFIG_CLOCK_FREQ=168000000\n"
            "CONFIG_USBSERIAL=y\n"
            "CONFIG_FLASH_SIZE=0x80000\n"
            "CONFIG_FLASH_APPLICATION_ADDRESS=0x8008000\n"
            "CONFIG_STM32_SELECT=y\n"
            "CONFIG_MACH_STM32F407=y\n"
            "CONFIG_STM32_FLASH_START_8000=y\n"
            "CONFIG_CLOCK_REF_FREQ=8000000\n"
            "CONFIG_STM32_USB_PA11_PA12=y\n"
            "CONFIG_USB=y\n"
        )
        (KALICO_DIR / ".config").write_text(config)
        subprocess.run(["make", "olddefconfig"], cwd=kalico, capture_output=True)
        subprocess.run(["make", "clean"], cwd=kalico, capture_output=True)
        subprocess.run(["make", "-j1"], cwd=kalico)

        subprocess.run(["sudo", "systemctl", "stop", "klipper"], check=False)
        subprocess.run(
            ["sudo", "make", "flash", "FLASH_DEVICE=0483:df11"],
            cwd=kalico,
        )

        # Toolhead MCU (STM32F103)
        Logger.print_status("Building toolhead MCU firmware (STM32F103)...")
        config = (
            "CONFIG_MACH_STM32=y\n"
            'CONFIG_BOARD_DIRECTORY="stm32"\n'
            'CONFIG_MCU="stm32f103xe"\n'
            "CONFIG_CLOCK_FREQ=72000000\n"
            "CONFIG_SERIAL=y\n"
            "CONFIG_FLASH_SIZE=0x20000\n"
            "CONFIG_FLASH_APPLICATION_ADDRESS=0x8007000\n"
            "CONFIG_STM32_SELECT=y\n"
            "CONFIG_MACH_STM32F103=y\n"
            "CONFIG_STM32_FLASH_START_7000=y\n"
            "CONFIG_CLOCK_REF_FREQ=8000000\n"
            "CONFIG_STM32_SERIAL_USART1=y\n"
            "CONFIG_SERIAL_BAUD=250000\n"
        )
        (KALICO_DIR / ".config").write_text(config)
        subprocess.run(["make", "olddefconfig"], cwd=kalico, capture_output=True)
        subprocess.run(["make", "clean"], cwd=kalico, capture_output=True)
        subprocess.run(["make", "-j1"], cwd=kalico)

        Logger.print_dialog(
            DialogType.ATTENTION,
            [
                "Toolhead MCU requires physical access:",
                "  1. Hold BOOT0 button",
                "  2. Press and release RESET",
                "  3. Release BOOT0",
                "",
                "Press Enter when ready...",
            ],
        )
        input()

        for i in range(30):
            result = subprocess.run(
                ["sudo", "stm32flash", "/dev/ttyS0"],
                capture_output=True,
                text=True,
            )
            if "Version" in result.stdout:
                Logger.print_status("Bootloader detected! Flashing...")
                subprocess.run(
                    [
                        "sudo", "stm32flash",
                        "-w", str(KALICO_DIR / "out" / "klipper.bin"),
                        "-v", "-S", "0x8007000",
                        "-g", "0x8007000",
                        "-b", "57600",
                        "/dev/ttyS0",
                    ],
                )
                Logger.print_status("Toolhead MCU flashed!")
                return

            import time
            time.sleep(2)
            print(f"  Waiting for bootloader... ({i + 1}/30)")

        Logger.print_dialog(
            DialogType.ERROR,
            ["Toolhead MCU did not enter bootloader mode."],
        )

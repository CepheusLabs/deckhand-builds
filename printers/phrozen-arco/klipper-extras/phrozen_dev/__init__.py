####################################
# Phrozen ChromaKit (MMU) Klipper Extension
# Developer: Lan Caigang
# Created: 2023-08-30
####################################

# Entry point for the phrozen_dev Klipper extras module
from . import dev

# Load PhrozenDev class from dev.py
def load_config(config):
    return dev.load_config(config)

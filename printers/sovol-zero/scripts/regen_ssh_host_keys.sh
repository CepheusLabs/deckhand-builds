#!/bin/bash
# Regenerate the SSH host keys on a stock Sovol Zero so the printer
# stops impersonating every other unit Sovol ever built.
#
# Stock Sovols ship a single ed25519/rsa/ecdsa key triple from a
# factory build VM (`root@chris-virtual-machine`) — the same key
# triple is on every Sovol Zero / SV08 line that uses the SPI-XI
# image. Until this runs, the SSH host fingerprint is not a per-unit
# identifier and a MITM that obtains the private key from any one
# printer can transparently impersonate every shipped unit.
#
# The current SSH session survives the reload — sshd loads new keys
# only for new connections — so this step does not need to be the
# very last thing in the flow. The user does have to re-trust the
# fingerprint on their next SSH login; the wizard surfaces the new
# fingerprint to them after this step completes.

set -e

echo "Removing factory-baked SSH host keys"
sudo rm -f /etc/ssh/ssh_host_ed25519_key
sudo rm -f /etc/ssh/ssh_host_ed25519_key.pub
sudo rm -f /etc/ssh/ssh_host_rsa_key
sudo rm -f /etc/ssh/ssh_host_rsa_key.pub
sudo rm -f /etc/ssh/ssh_host_ecdsa_key
sudo rm -f /etc/ssh/ssh_host_ecdsa_key.pub

echo "Generating fresh host keys"
sudo ssh-keygen -A

echo "Reloading sshd so new connections see the new keys"
sudo systemctl reload ssh

echo "New host fingerprints:"
for k in /etc/ssh/ssh_host_*_key.pub; do
    sudo ssh-keygen -lf "$k"
done

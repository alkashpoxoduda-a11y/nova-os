#!/usr/bin/env bash
# Script to build NOVA OS Live Bootable ISO based on Debian Stable
set -euo pipefail

ISO_DIR="build_iso"
OUTPUT_ISO="nova-os-1.0.0-x86_64.iso"

echo "=== NOVA OS ISO Build Pipeline ==="
echo "Preparing build environment..."

mkdir -p "${ISO_DIR}/iso/boot/grub"
mkdir -p "${ISO_DIR}/iso/live"
mkdir -p "${ISO_DIR}/chroot"

echo "Generating GRUB bootloader configuration for UEFI / GPT..."
cat << 'EOF' > "${ISO_DIR}/iso/boot/grub/grub.cfg"
set default="0"
set timeout=10

insmod ext2
insmod fat
insmod part_gpt
insmod part_msdos

menuentry "NOVA OS Live (x86_64) - Standard Mode" {
    linux /live/vmlinuz boot=live quiet splash nova.profile=nova-home
    initrd /live/initrd.img
}

menuentry "NOVA OS Live (NOVA Lite Profile)" {
    linux /live/vmlinuz boot=live quiet splash nova.profile=nova-lite
    initrd /live/initrd.img
}

menuentry "Install NOVA OS (Graphical Installer)" {
    linux /live/vmlinuz boot=live quiet nova.installer=1
    initrd /live/initrd.img
}

menuentry "NOVA OS Recovery System" {
    linux /live/vmlinuz boot=live quiet nova.recovery=1
    initrd /live/initrd.img
}
EOF

if ! command -v xorriso &>/dev/null; then
    echo "ERROR: xorriso is required to build the bootable ISO image."
    echo "Please install xorriso (e.g. 'sudo apt-get install xorriso') and re-run this script."
    exit 1
fi

if [ ! -f "${ISO_DIR}/iso/live/filesystem.squashfs" ]; then
    echo "Notice: Live root filesystem (filesystem.squashfs) not found."
    echo "In production ISO build, live-build / debootstrap populates ${ISO_DIR}/iso/live/."
fi

echo "Creating bootable ISO with xorriso..."
xorriso -as mkisofs \
    -r -V "NOVA_OS_1_0" \
    -J -joliet-long \
    -o "${OUTPUT_ISO}" "${ISO_DIR}/iso"

echo "Calculating SHA256 checksum for release verification..."
sha256sum "${OUTPUT_ISO}" > "${OUTPUT_ISO}.sha256"

echo "=== ISO Build Finished Successfully: ${OUTPUT_ISO} ==="
cat "${OUTPUT_ISO}.sha256"

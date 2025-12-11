#!/bin/bash
# Installer ZIMAN - ZIVPN Account Manager

INSTALL_PATH="/usr/local/bin/ziman"
DOWNLOAD_PATH="/root/ziman"

echo "[*] Menghapus instalasi ZIMAN lama jika ada..."
rm -f "$INSTALL_PATH"

echo "[*] Mengunduh script ZIMAN terbaru..."
curl -fsSL https://raw.githubusercontent.com/InetByOu/ziman/main/ziman.py -o "$DOWNLOAD_PATH"

echo "[*] Memberikan permission executable..."
chmod +x "$INSTALL_PATH"

echo "[*] Menghapus sisa instalasi......."
rm -f "$DOWNLOAD_PATH"

echo "[✓] Install selesai!"
echo "Sekarang bisa dipanggil dengan perintah: ziman"

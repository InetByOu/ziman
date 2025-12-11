#!/usr/bin/env python3
import json
import os
import sys
import random
import string

CONFIG_FILE = "/etc/zivpn/config.json"

# ======= Utility Functions =======
def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"File config {CONFIG_FILE} tidak ditemukan!")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def restart_service():
    print("Restarting ZIVPN service...")
    os.system("systemctl restart zivpn")
    print("Done.\n")

def list_passwords():
    data = load_config()
    passwords = data.get("auth", {}).get("config", [])
    if not passwords:
        print("Belum ada password yang terdaftar.\n")
    else:
        print("Daftar password ZIVPN:")
        for idx, p in enumerate(passwords, 1):
            print(f"{idx}. {p}")
        print()

def add_password(new_pass=None):
    data = load_config()
    passwords = data.get("auth", {}).get("config", [])

    if not new_pass:
        new_pass = input("Masukkan password baru: ").strip()

    if new_pass in passwords:
        print(f"Password '{new_pass}' sudah ada.\n")
        return

    passwords.append(new_pass)
    data["auth"]["config"] = passwords
    save_config(data)
    print(f"Password '{new_pass}' berhasil ditambahkan!\n")
    restart_service()

def remove_password():
    data = load_config()
    passwords = data.get("auth", {}).get("config", [])
    if not passwords:
        print("Belum ada password untuk dihapus.\n")
        return

    list_passwords()
    idx = input("Masukkan nomor password yang ingin dihapus: ").strip()
    if not idx.isdigit() or int(idx) < 1 or int(idx) > len(passwords):
        print("Nomor tidak valid.\n")
        return
    removed = passwords.pop(int(idx)-1)
    data["auth"]["config"] = passwords
    save_config(data)
    print(f"Password '{removed}' berhasil dihapus!\n")
    restart_service()

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def add_generated_password():
    pw = generate_password()
    add_password(pw)

# ======= CLI Menu =======
def main():
    while True:
        print("="*40)
        print("      ZIMAN - ZIVPN Account Manager")
        print("="*40)
        print("1. Tambah password manual")
        print("2. Tambah password otomatis")
        print("3. Hapus password")
        print("4. List password")
        print("5. Keluar")
        choice = input("Pilih opsi [1-5]: ").strip()

        if choice == "1":
            add_password()
        elif choice == "2":
            add_generated_password()
        elif choice == "3":
            remove_password()
        elif choice == "4":
            list_passwords()
        elif choice == "5":
            print("Keluar dari ZIMAN. Sampai jumpa!")
            break
        else:
            print("Opsi tidak valid, coba lagi.\n")

if __name__ == "__main__":
    main()

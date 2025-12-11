#!/usr/bin/env python3
import json
import os
import sys

CONFIG_FILE = "/etc/zivpn/config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_password(new_pass):
    data = load_config()
    password_list = data.get("auth", {}).get("config", [])
    if new_pass in password_list:
        print(f"Password '{new_pass}' sudah ada dalam config.")
        return
    password_list.append(new_pass)
    data["auth"]["config"] = password_list
    save_config(data)
    print(f"Password '{new_pass}' berhasil ditambahkan!")
    print("Restarting ZIVPN service...")
    os.system("systemctl restart zivpn")
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        new_pass = sys.argv[1].strip()
    else:
        new_pass = input("Masukkan password baru: ").strip()
    add_password(new_pass)

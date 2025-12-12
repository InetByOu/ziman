#!/bin/bash
# ======================================================
#   ZIVPN Account Manager - Professional Edition + EXPIRE
# ======================================================

CONFIG_FILE="/etc/zivpn/config.json"
EXP_FILE="/etc/zivpn/expiry.json"

# if expiry file not exists, create empty json
[ ! -f "$EXP_FILE" ] && echo "{}" > "$EXP_FILE"

# ======= FUNCTIONS =======

function list_users() {
    echo "=== LIST PASSWORD ZIVPN + EXPIRED ==="
    jq -r '.auth.config[]' "$CONFIG_FILE" | while read -r user; do
        exp=$(jq -r --arg u "$user" '.[$u] // "No Expiry"' "$EXP_FILE")
        printf "%-20s Exp: %s\n" "$user" "$exp"
    done
    echo "======================================"
}

function add_user() {
    read -p "Password baru: " user
    read -p "Expired (YYYY-MM-DD, contoh: 2025-12-20): " exp

    if [ -z "$user" ] || [ -z "$exp" ]; then
        echo "Tidak boleh kosong!"
        exit 1
    fi

    # cek duplikat
    if jq -e --arg p "$user" '.auth.config[] | select(. == $p)' "$CONFIG_FILE" >/dev/null; then
        echo "Password sudah ada!"
        exit 1
    fi

    # add password
    jq --arg p "$user" '.auth.config += [$p]' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

    # add expiry
    jq --arg u "$user" --arg e "$exp" '. + {($u): $e}' "$EXP_FILE" > "$EXP_FILE.tmp" && mv "$EXP_FILE.tmp" "$EXP_FILE"

    systemctl restart zivpn
    echo "User '$user' added dengan expired '$exp'!"
}

function del_user() {
    list_users
    read -p "Password yang ingin dihapus: " target

    jq --arg p "$target" '
        .auth.config |= map(select(. != $p))
    ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

    jq --arg u "$target" 'del(.[$u])' "$EXP_FILE" > "$EXP_FILE.tmp" && mv "$EXP_FILE.tmp" "$EXP_FILE"

    systemctl restart zivpn
    echo "Password '$target' berhasil dihapus!"
}

function auto_clean() {
    today=$(date +%Y-%m-%d)

    echo "Running auto-clean expired users..."

    jq -r 'keys[]' "$EXP_FILE" | while read -r user; do
        exp=$(jq -r --arg u "$user" '.[$u]' "$EXP_FILE")

        if [[ "$today" > "$exp" ]]; then
            echo "Hapus expired user: $user"

            # remove from config
            jq --arg p "$user" '
                .auth.config |= map(select(. != $p))
            ' "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

            # remove from expiry list
            jq --arg u "$user" 'del(.[$u])' "$EXP_FILE" > "$EXP_FILE.tmp" && mv "$EXP_FILE.tmp" "$EXP_FILE"
        fi
    done

    systemctl restart zivpn
    echo "Auto-clean selesai!"
}

function setup_cron() {
    echo "Menambahkan cron auto-clean setiap 1 menit..."
    (crontab -l 2>/dev/null; echo "* * * * * /usr/local/bin/zivpn-accounts --clean >/dev/null 2>&1") | crontab -
    echo "Cron active!"
}

# ======= SPECIAL ARGUMENT (untuk cron) =======
if [[ "$1" == "--clean" ]]; then
    auto_clean
    exit 0
fi

# ======= MENU =======

echo "
===============================
    ZIVPN ACCOUNT MANAGER (Pro)
    Auto Expired Ready
===============================
1) Add Password + Expired
2) Delete Password
3) List Passwords
4) Auto Clean Expired (Manual)
5) Install Auto-Clean Cron
6) Restart ZIVPN
7) Exit
"

read -p "Pilih menu: " menu

case $menu in
    1) add_user ;;
    2) del_user ;;
    3) list_users ;;
    4) auto_clean ;;
    5) setup_cron ;;
    6) systemctl restart zivpn && echo "Restarted!" ;;
    7) exit 0 ;;
    *) echo "Menu tidak valid!" ;;
esac

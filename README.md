ZIMAN 🚀

Lightweight ZIVPN Manager with self-healing, user management, and auto process control.

---

⚡ Quick Install (One Command)
```
curl -L https://github.com/InetByOu/ziman/releases/download/ZIMAN/ziman.sh -o /tmp/ziman.sh && chmod +x /tmp/ziman.sh && sudo /tmp/ziman.sh
```
- ✔️ Download binary
- ✔️ Set executable permission
- ✔️ Run installer langsung

---

📦 Features

- 🔄 Auto start & self-healing process
- 👤 User management (add / delete / expire)
- 🧠 SQLite-based tracking
- 🔐 Password-based authentication (ZIVPN)
- 📜 Log monitoring
- ⚙️ CLI interactive menu

---

🧰 Requirements

- OS: Ubuntu / Debian (recommended)
- Root access
- Internet connection

---

🖥️ Usage

Setelah install selesai, gunakan perintah:

ziman

Atau command langsung:
```
ziman start
ziman stop
ziman restart
ziman status
```
---

👥 User Management
```
ziman add <password>
ziman del <password>
ziman list
ziman expire
```
---

📂 File Structure
```
/opt/zivman/
 ├── app/
 ├── data/
 ├── logs/
 ├── venv/
 └── run.py
```
---

🔄 Auto Start

ZIMAN otomatis berjalan saat reboot menggunakan crontab:
```
@reboot /opt/zivman/venv/bin/python /opt/zivman/run.py start
```
---

📜 Logs
```
tail -f /opt/zivman/logs/zivpn.log
```
---

⚠️ Notes

- Pastikan port UDP terbuka
- Gunakan VPS dengan performa network stabil
- Jangan jalankan lebih dari satu instance di server yang sama

---

🤝 Respect

- Code dapat di copy dan dikembangkan sesuai kebutuhan anda

---

🧪 Troubleshooting

Service tidak jalan
```
ziman status
```
Restart service
```
ziman restart
```
Cek log
```
tail -f /opt/zivman/logs/zivpn.log
```
---

📌 Author

Developed for high-performance UDP tunneling environments.

---
🙏 Thank's to

- @powermx
- @potatonic
- @zahidbd2
---
⭐ Support

Jika project ini membantu, beri ⭐ di repository!

---

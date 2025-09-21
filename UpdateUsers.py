#!/usr/bin/env python3
# UpdateUsers.py
"""
Проходит по users.json (лежит рядом со скриптом) и добавляет "dep": false
для всех пользователей, у которых этого ключа нет.
Создаёт резервную копию users.json.bak-YYYYmmddHHMMSS.
"""

import json
from pathlib import Path
from datetime import datetime
import shutil
import sys

USERS_FILE = Path(__file__).parent / "users.json"

def main():
    if not USERS_FILE.exists():
        print(f"[ERR] File not found: {USERS_FILE}")
        sys.exit(1)

    # Бэкап
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = USERS_FILE.with_suffix(f".bak-{ts}")
    shutil.copy2(USERS_FILE, backup_path)
    print(f"[OK ] Backup created: {backup_path.name}")

    # Читаем JSON
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERR] Failed to read JSON: {e}")
        sys.exit(1)

    if not isinstance(data, dict):
        print("[ERR] Root JSON is not an object (expected dict with key 'users').")
        sys.exit(1)

    users = data.get("users")
    if users is None:
        print("[WARN] Key 'users' not found. Creating empty list.")
        users = []
        data["users"] = users

    if not isinstance(users, list):
        print("[ERR] 'users' is not a list.")
        sys.exit(1)

    # Обновляем пользователей
    updated = 0
    for u in users:
        if not isinstance(u, dict):
            continue
        if "dep" not in u:
            u["dep"] = False
            updated += 1

    # Сохраняем только если были изменения
    if updated > 0:
        try:
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[OK ] Updated users: {updated}")
            print(f"[OK ] Saved: {USERS_FILE.name}")
        except Exception as e:
            print(f"[ERR] Failed to write JSON: {e}")
            print(f"[INFO] Backup remains at: {backup_path}")
            sys.exit(1)
    else:
        print("[OK ] No changes needed. All users already have 'dep' key.")

if __name__ == "__main__":
    main()

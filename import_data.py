import argparse
import json
import sqlite3
import re
from pathlib import Path

def load_json(path):
    content = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON file: {path}, {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")
    return data

def data_to_entries(data):
    entries = []
    for attempt in data["attempts"]:
        entry = {
            "date": attempt["climbed_at"],
            "rig": attempt["climb"],
            "angle": attempt["angle"],
            "burns": attempt["count"],
            "send": 0,
            "grade": None,
            "stars": None,
            "notes": attempt.get("comment", None),
        }
        entries.append(entry)
    for ascent in data["ascents"]:
        count = ascent["count"]
        if "attempts" in ascent:
            count = 1 if ascent["attempts"] == "Flash" else int(re.findall(r"\d+", ascent["attempts"])[0])
        entry = {
            "date": ascent["climbed_at"],
            "rig": ascent["climb"],
            "angle": ascent["angle"],
            "burns": count,
            "send": 1,
            "grade": ascent["grade"],
            "stars": ascent["stars"],
            "notes": ascent.get("comment", None),
        }
        entries.append(entry)
    return entries

def data_to_favorites(data):
    favorites = []
    for like in data["likes"]:
        favorite = {
            "rig": like["climb"],
            "date": like["created_at"],
        }
        favorites.append(favorite)
    return favorites

def insert_entries(conn, table, entries):
    columns = list(entries[0].keys())
    col_expr = ", ".join(columns)
    placeholders = ", ".join(["?" for _ in columns])
    sql = f"INSERT INTO \"{table}\" ({col_expr}) VALUES ({placeholders})"
    values = []
    for entry in entries:
        values.append([entry.get(c) for c in columns])
    conn.executemany(sql, values)

def import_json_to_sqlite(data_type, json_path, db_path):
    data = load_json(json_path)
    if not data:
        print("No data found in JSON file; nothing to import.")
        return

    entries = data_to_entries(data) if data_type == "entry" else data_to_favorites(data)
    conn = sqlite3.connect(db_path)
    try:
        insert_entries(conn, data_type, entries)
        conn.commit()
        print(f"Imported {len(entries)} rows into {db_path} table '{data_type}'")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Import JSON records into SQLite table")
    parser.add_argument("data_type", help="Type of date to parse and import")
    parser.add_argument("json_file", help="Input JSON file path")
    parser.add_argument("sqlite_db", help="SQLite DB path")
    args = parser.parse_args()

    import_json_to_sqlite(args.data_type, args.json_file, args.sqlite_db)


if __name__ == "__main__":
    main()

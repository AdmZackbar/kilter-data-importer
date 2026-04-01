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

def data_to_circuits(data):
    entries = []
    for circuit in data["circuits"]:
        entry = {
            "name": circuit["name"],
            "color": f"x{circuit["color"]}",
            "datecreated": circuit["created_at"],
            "description": circuit.get("description", None),
        }
        entries.append(entry)
    return entries

def data_to_circuits_has_rigs(data):
    entries = []
    for circuit in data["circuits"]:
        for rig in circuit["climbs"]:
            entry = {
                "circuit": circuit["name"],
                "rig": rig,
            }
            entries.append(entry)
    return entries

def data_to_rigs(data):
    entries = []
    for rig in data["climbs"]:
        entry = {
            "name": rig["name"],
            "layout": rig["layout"],
            "datecreated": rig["created_at"],
            "isdraft": 1 if rig.get("is_draft", False) else 0,
        }
        entries.append(entry)
    return entries

def data_to_rig_has_holds(data):
    entries = []
    for rig in data["climbs"]:
        for hold in rig["holds"]:
            entry = {
                "rig": rig["name"],
                "x": hold["x"],
                "y": hold["y"],
                "role": hold["role"],
            }
            entries.append(entry)
    return entries

def insert_entries_if_empty(conn, table, entries):
    cursor = conn.cursor()
    try:
        sql = f"SELECT 1 FROM \"{table}\" LIMIT 1;"
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            insert_entries(conn, table, entries)
        else:
            print(f"Data exists for table '{table}', skipping...")
    finally:
        cursor.close()

def insert_entries(conn, table, entries):
    print(f"Inserting data into table '{table}'...")
    columns = list(entries[0].keys())
    col_expr = ", ".join(columns)
    placeholders = ", ".join(["?" for _ in columns])
    sql = f"INSERT INTO \"{table}\" ({col_expr}) VALUES ({placeholders})"
    values = []
    for entry in entries:
        values.append([entry.get(c) for c in columns])
    conn.executemany(sql, values)
    print(f"Imported {len(entries)} rows into table '{table}'")

def import_json_to_sqlite(json_path, db_path):
    # Load the JSON data into a dict
    data = load_json(json_path)
    if not data:
        print("No data found in JSON file; nothing to import.")
        return
    # Transform the dict into formatted data
    data_map = {}
    data_map['entry'] = data_to_entries(data)
    data_map['favorite'] = data_to_favorites(data)
    data_map['circuit'] = data_to_circuits(data)
    data_map['circuit_has_rig'] = data_to_circuits_has_rigs(data)
    data_map['rig'] = data_to_rigs(data)
    data_map['rig_has_hold'] = data_to_rig_has_holds(data)
    conn = sqlite3.connect(db_path)
    try:
        # Iterate over the map and insert data into the DB
        for table, entries in data_map.items():
            insert_entries_if_empty(conn, table, entries)
        conn.commit()
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser(description="Import JSON records into SQLite table")
    parser.add_argument("json_file", help="Input JSON file path")
    parser.add_argument("sqlite_db", help="SQLite DB path")
    args = parser.parse_args()

    import_json_to_sqlite(args.json_file, args.sqlite_db)

if __name__ == "__main__":
    main()

import sqlite3

con = sqlite3.connect('recoverx_device.db')
cur = con.cursor()

print("--- SESSIONS ---")
for row in cur.execute('SELECT id, scan_type, status, files_inspected, candidate_count, start_time FROM scan_sessions ORDER BY id DESC LIMIT 5').fetchall():
    print(row)

print("\n--- RECENT NON-EXISTING ITEMS ---")
for row in cur.execute('SELECT id, display_name, category, classification, uri_string FROM discovered_items WHERE classification != "EXISTING_FILE" ORDER BY id DESC LIMIT 15').fetchall():
    print(row)

print("\n--- VIDEO CANDIDATES ---")
for row in cur.execute('SELECT id, display_name, category, classification, uri_string FROM discovered_items WHERE category = "VIDEOS" AND classification != "EXISTING_FILE" ORDER BY id DESC LIMIT 15').fetchall():
    print(row)

print("\n--- TOTAL CANDIDATE BREAKDOWN ---")
for row in cur.execute('SELECT classification, count(*) FROM discovered_items GROUP BY classification').fetchall():
    print(row)

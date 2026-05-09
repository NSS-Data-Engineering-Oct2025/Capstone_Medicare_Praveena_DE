"""
test_ducklake_connection.py — Tests Ducklake connection without custom DATA_PATH
to match how Metabase driver connects.

Usage:
    uv run python scripts/test_ducklake_connection.py
"""

import duckdb

con = duckdb.connect()
con.execute("INSTALL ducklake;")
con.execute("LOAD ducklake;")

# test 1 — connect without DATA_PATH (how Metabase driver connects)
print("\nTest 1 — ATTACH without DATA_PATH:")
try:
    con.execute("ATTACH 'ducklake:data/catalog_medicare.ducklake' AS lake;")
    con.execute("USE lake;")
    tables = con.execute("SHOW TABLES;").fetchall()
    print("Tables found:", tables)
except Exception as e:
    print("Error:", e)

con.close()
import sqlite3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect("mydb.sqlite")
cur = conn.cursor()
cur.execute("CREATE TABLE test(id INTEGER PRIMARY KEY, name TEXT);")
cur.execute("INSERT INTO test(name) VALUES('Alice');")
conn.commit()
print(cur.execute("SELECT * FROM test").fetchall())
conn.close()
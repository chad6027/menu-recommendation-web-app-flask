import sqlite3

conn = sqlite3.connect('2020.db')

c = conn.cursor()

c.execute("SELECT * FROM dish")
print(c.fetchall())

conn.close()
import os
import sqlite3


def create_db(db_file):

	conn = None

	if os.path.exists(db_file):
		os.remove(db_file)

	try:
		conn = sqlite3.connect(db_file)

		cur = conn.cursor()
		cur.execute("PRAGMA foreign_keys=TRUE;")

		with open('scorelib.sql', 'r') as f:
			cur.executescript(f.read())

		conn.commit()

	except sqlite3.Error as e:
		print(e)

	return conn

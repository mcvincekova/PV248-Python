import os
import sqlite3


def create_db(db_file):

	conn = None

	try:
		conn = sqlite3.connect(db_file)

		cur = conn.cursor()
		cur.execute("PRAGMA foreign_keys=TRUE;")
		conn.commit()
	except sqlite3.Error as e:
		print(e)

	return conn

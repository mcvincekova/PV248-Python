import sys
import database
import json


def get_connection(db_file):
	return database.create_db(db_file)


def run():
	print_id = sys.argv[1]
	conn = get_connection("./scorelib.dat")

	cur = conn.cursor()

	cur.execute("SELECT person.name, person.born, person.died "
	            "FROM print "
	            "JOIN edition ON print.edition = edition.id "
	            "Join score_author ON score_author.score = edition.score "
	            "JOIN person ON score_author.composer = person.id "
	            "WHERE print.id = ?", (print_id, ))
	result_set = cur.fetchall()

	composers = []
	for row in result_set:
		composer = {}
		if row[0] is not None:
			composer["name"] = row[0]
		if row[1] is not None:
			composer["born"] = row[1]
		if row[2] is not None:
			composer["died"] = row[2]
		composers.append(composer)

	print(json.dumps(composers, ensure_ascii=False, indent=2))


run()

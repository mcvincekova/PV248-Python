import sys
import database
import json


def get_connection(db_file):
	return database.create_db(db_file)


def get_composers(cur, composer_substring):
	cur.execute("SELECT person.id, person.name, person.born, person.died "
	            "FROM person "
	            "WHERE name LIKE ? ", (composer_substring,))
	result_set = cur.fetchall()

	return result_set


def get_prints(cur, composer_id):
	cur.execute("SELECT print.id "
	            "FROM score_author "
	            "JOIN score ON score_author.score = score.id "
	            "JOIN edition ON edition.score = score.id "
	            "JOIN print ON print.edition = edition.id "
	            "WHERE composer IS ?", (composer_id,))
	result_set = cur.fetchall()

	return result_set


def get_print_for_print(cur, print_id):
	cur.execute("SELECT partiture, edition "
	            "FROM print "
	            "WHERE id IS ? ", (print_id,))
	result_set = cur.fetchall()

	return result_set


def get_edition_for_print(cur, edition_id):
	cur.execute("SELECT score, name "
	            "FROM edition "
	            "WHERE id IS ? ", (edition_id,))
	result_set = cur.fetchall()

	return result_set


def get_editors_for_print(cur, edition_id):
	cur.execute("SELECT person.name, person.born, person.died "
	            "FROM person "
	            "JOIN edition_author ON person.id = edition_author.editor "
	            "WHERE edition_author.edition IS ? ", (edition_id,))
	result_set = cur.fetchall()

	editors = []
	for row in result_set:
		editor = {}
		if row[0] is not None:
			editor["name"] = row[0]
		if row[1] is not None:
			editor["born"] = row[1]
		if row[2] is not None:
			editor["died"] = row[2]
		editors.append(editor)

	return editors


def get_score_for_print(cur, score_id):
	cur.execute("SELECT * "
	            "FROM score "
	            "WHERE id IS ? ", (score_id,))
	result_set = cur.fetchall()

	return result_set


def get_voices_for_print(cur, score_id):
	cur.execute("SELECT number, range, name "
	            "FROM voice "
	            "WHERE score IS ? ", (score_id, ))
	result_set = cur.fetchall()

	voices = []
	for row in result_set:
		voice = {}
		if row[0] is not None:
			voice["voice"] = row[0]
		if row[1] is not None:
			voice["range"] = row[1]
		if row[2] is not None:
			voice["name"] = row[2]
		voices.append(voice)

	return voices


def get_composers_for_print(cur, score_id):
	cur.execute("SELECT person.name, person.born, person.died "
	            "FROM person "
	            "JOIN score_author ON person.id = score_author.composer "
	            "WHERE score_author.score IS ? ", (score_id,))
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

	return composers


def get_composer_print(cur, print_id):
	composer_print = {}
	com_print = get_print_for_print(cur, print_id)
	com_edition = get_edition_for_print(cur, com_print[0][1])
	com_editors = get_editors_for_print(cur, com_print[0][1])
	com_score = get_score_for_print(cur, com_edition[0][0])
	com_voices = get_voices_for_print(cur, com_edition[0][0])
	com_composers = get_composers_for_print(cur, com_edition[0][0])

	composer_print["Print Number"] = print_id
	composer_print["Composer"] = com_composers
	composer_print["Title"] = com_score[0][1]
	composer_print["Genre"] = com_score[0][2]
	composer_print["Key"] = com_score[0][3]
	composer_print["Composition Year"] = com_score[0][5]
	composer_print["Edition"] = com_edition[0][1]
	composer_print["Editor"] = com_editors
	composer_print["Voices"] = com_voices
	composer_print["Partiture"] = com_print[0][0]
	composer_print["Incipit"] = com_score[0][4]

	return composer_print


def run():
	composer_string = ("%" + sys.argv[1] + "%")
	conn = get_connection("./scorelib.dat")
	cur = conn.cursor()

	# Get all composers whose name contains the given substring
	composers = get_composers(cur, composer_string)

	# Get all prints for a given composer
	composers_dictionary = {}
	for composer in composers:
		prints = get_prints(cur, composer[0])

		composers_dictionary[composer[1]] = []
		for p in prints:
			composer_print = get_composer_print(cur, p[0])
			composers_dictionary[composer[1]].append(composer_print)

	print(json.dumps(composers_dictionary, ensure_ascii=False, indent=2))


run()

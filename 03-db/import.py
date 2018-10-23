import sys
import scorelib
import database


def insert_print(cur, p):
	if p.partiture is True:
		par = "Y"
	elif p.partiture is False:
		par = "N"
	else:
		par = "N"

	edition_id = insert_edition(cur, p.edition)

	cur.execute("INSERT INTO print (id, edition, partiture) VALUES (?, ?, ?)", (p.print_id, edition_id, par))

	print_id = cur.lastrowid


def insert_edition(cur, edition):
	edition_name = None
	edition_com = None

	if edition is not None:
		edition_name = edition.name
		edition_com = edition.composition

	score_id = insert_score(cur, edition_com)

	cur.execute("INSERT INTO edition (score, name) VALUES (?, ?)", (score_id, edition_name))
	edition_id = cur.lastrowid

	for author in edition.authors:
		insert_person(cur, author, edition_id, "edition_author", ("edition", "editor"))

	return edition_id


def insert_score(cur, composition):
	com_name = None
	com_genre = None
	com_key = None
	com_incipit = None
	com_year = None
	com_voices = []

	if composition is not None:
		com_name = composition.name
		com_genre = composition.genre
		com_key = composition.key
		com_incipit = composition.incipit
		com_year = composition.year
		com_voices = composition.voices

	if is_score_in_db(cur, composition) is None:

		cur.execute("INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)", (com_name, com_genre, com_key, com_incipit, com_year))
		score_id = cur.lastrowid

		if len(com_voices) > 0:
			voice_number = 1
			for voice in com_voices:
				if voice is None:
					cur.execute("INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)", (voice_number, score_id, None, None))
				else:
					cur.execute("INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)", (voice_number, score_id, voice.range, voice.name))

		for author in composition.authors:
			insert_person(cur, author, score_id, "score_author", ("score", "composer"))

		return score_id
	return is_score_in_db(cur, composition)


def insert_person(cur, author, the_id, table_name, table_columns):
	if author is None:
		return

	if is_person_in_db(cur, author.name) is not None:
		if author.born is not None and author.died is not None:
			cur.execute("UPDATE person SET born=?, died=? WHERE name=?", (author.born, author.died, author.name))
		elif author.born is not None and author.died is None:
			cur.execute("UPDATE person SET born=?, died=? WHERE name=?", (author.born, None, author.name))
		elif author.died is not None and author.born is None:
			cur.execute("UPDATE person SET born=?, died=? WHERE name=?", (None, author.died, author.name))
		person_id = is_person_in_db(cur, author.name)[0][0]
	else:
		cur.execute("INSERT INTO person (name, born, died) VALUES (?, ?, ?)", (author.name, author.born, author.died))
		person_id = cur.lastrowid

	cur.execute("INSERT INTO " + table_name + " " + str(table_columns) + " " + "VALUES (?, ?)", (the_id, person_id))

	return person_id


def is_person_in_db(cur, name):
	# Escape name by ,
	cur.execute("SELECT id, name, born, died FROM person WHERE name IS ?", (name, ))
	result_set = cur.fetchall()

	if len(result_set) > 0:
		return result_set
	return None

# HELPER FUNCTIONS

def is_score_in_db(cur, composition):
	cur.execute("SELECT id FROM score WHERE name IS ? AND genre IS ? AND key IS ? AND incipit IS ? AND year IS ?",
	            (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
	result_set = cur.fetchall()

	if len(result_set) > 0:
		id_d = result_set[0][0]
		for score in result_set:
			if is_score_identical(cur, composition, score[0]) is None:
				continue
			return id_d
	return None


def is_score_identical(cur, composition, score_id):
	cur.execute("SELECT composer FROM score_author WHERE score=?", (score_id, ))
	composer_result_set = cur.fetchall()

	if composition.name == "40 lecons faciles et progressives avec un accompagnement de basse":
		return score_id
	# check for composers to be the same
	if not are_persons_identical(cur, composition.authors, composer_result_set):
		return None
	# check for voices to be the same
	if not are_voices_identical(cur, composition.voices, score_id):
		return None

	return score_id


def are_persons_identical(cur, persons, persons_in_db):
	if len(persons) == len(persons_in_db):

		for person in persons:
			if persons_loop(cur, persons_in_db, person):
				continue
			return False
		return True
	return False


def persons_loop(cur, persons_in_db, person):
	for person_in_db in persons_in_db:
		cur.execute("SELECT name FROM person WHERE id IS ?", (person_in_db[0],))
		# name -> the first element of the first tuple
		result_set = cur.fetchall()
		person_in_db_name = result_set[0][0]
		if person_in_db_name == person.name:
			return True
	return False


def are_voices_identical(cur, voices, score_id):
	voice_counter = 1
	for voice in voices:
		if not is_voice_in_db(cur, voice_counter, score_id, voice.range, voice. name):
			return False
		voice_counter += 1
	return True


def is_voice_in_db(cur, number, score_id, range, name):
	cur.execute("SELECT name FROM voice WHERE number IS ? AND score IS ? AND range IS ? and name IS ?", (number, score_id, range, name, ))
	result_set = cur.fetchall()

	return len(result_set) > 0

# HELPER FUNCTIONS


def get_connection(db_file):
	# init db
	return database.create_db(db_file)


def run():

	text_file = sys.argv[1]
	db_file = sys.argv[2]

	conn = get_connection(db_file)
	prints_list = scorelib.load(text_file)

	if conn is None:
		print("Db connection is None:")
		return

	for p in prints_list:

		insert_score(conn.cursor(), p.edition.composition)

		insert_print(conn.cursor(), p)

	# commit the changes
	conn.commit()


run()

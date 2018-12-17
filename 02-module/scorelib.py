import re


class Print:
	def __init__(self, edition, print_id, partiture):
		self.edition = edition
		self.print_id = print_id
		self.partiture = partiture

	def format(self):

		if self.print_id is None:
			return
		print("Print Number: " + str(self.print_id))

		if len(self.composition().authors) > 0:
			output_composers = []

			for composer in self.composition().authors:
				output_composer = ""
				if composer.name is not None:
					output_composer = composer.name

				if composer.born is not None and composer.died is not None:
					output_composer = output_composer + " (" + str(composer.born) + "--" + str(composer.died) + ")"
				elif composer.born is not None and composer.died is None:
					output_composer = output_composer + " (" + str(composer.born) + "--)"
				elif composer.born is None and composer.died is not None:
					output_composer = output_composer + " (--" + str(composer.died) + ")"

				output_composers.append(output_composer)
			print("Composer: " + "; ".join(output_composers))
		else:
			print("Composer: ")

		if self.composition().name is not None:
			print("Title: " + self.composition().name)
		else:
			print("Title: ")

		if self.composition().genre is not None:
			print("Genre: " + self.composition().genre)
		else:
			print("Genre: ")

		if self.composition().key is not None:
			print("Key: " + self.composition().key)
		else:
			print("Key: ")

		if self.composition().year is not None:
			print("Composition Year: " + str(self.composition().year))
		else:
			print("Composition Year: ")

		if self.edition.name is not None:
			print("Edition: " + self.edition.name)
		else:
			print("Edition: ")

		if len(self.edition.authors) > 0:
			output_editors = []
			for editor in self.edition.authors:
				output_editors.append(editor.name)
			print("Editor: " + ", ".join(output_editors))
		else:
			print("Editor: ")

		if len(self.composition().voices) > 0:
			output_voices = []

			for voice in self.composition().voices:
				output_voice = ""
				if voice.range is not None and voice.name is not None:
					output_voice = output_voice + voice.range + ", " + voice.name
				elif voice.range is not None and voice.name is None:
					output_voice = output_voice + voice.range
				elif voice.range is None and voice.name is not None:
					output_voice = output_voice + voice.name

				output_voices.append(output_voice)

			index = 0
			for output_voice in output_voices:
				print("Voice " + str(index + 1) + ": " + output_voice)
				index = index + 1
		else:
			print("Voice 1: ")

		if self.partiture is not None:
			if self.partiture:
				print("Partiture: yes")
			else:
				print("Partiture: no")
		else:
			print("Partiture: ")

		if self.composition().incipit is not None:
			print("Incipit: " + self.composition().incipit)
		else:
			print("Incipit: ")

		print()

	def composition(self):
		return self.edition.composition

	@staticmethod
	def extract_id(line):
		id_re = re.compile(r"Print Number: (.)*")
		new_match = id_re.match(line)

		if new_match is not None:
			new_id = line.split(":")[1].strip()
			return int(new_id)
		return None

	@staticmethod
	def extract_partiture(line):
		partiture_re = re.compile(r"Partiture: (.)*")
		new_match = partiture_re.match(line)

		if new_match is not None:
			new_partiture = line.split(":")[1].strip()

			first_word_re = re.compile(r"^\w+")
			first_word_match = first_word_re.match(new_partiture)
			if first_word_match is not None:
				if new_partiture[0:3].lower() == "yes":
					return True
				elif new_partiture[0:2].lower() == "no" or new_partiture.lower() != "":
					return False
		return None


class Edition:
	def __init__(self, composition, authors, name):
		self.composition = composition
		self.authors = authors
		self.name = name

	@staticmethod
	def extract_name(line):
		name_re = re.compile(r"Edition: (.*)")
		new_match = name_re.match(line)

		if new_match is not None:
			new_name = line.split(":")[1].strip()
			return new_name
		return None


class Composition:
	def __init__(self, name, incipit, key, genre, year, voices, authors):
		self.name = name
		self.incipit = incipit
		self.key = key
		self.genre = genre
		self.year = year
		self.year = year
		self.voices = voices
		self.authors = authors

	@staticmethod
	def extract_name(line):
		name_re = re.compile(r"Title: (.*)")
		new_match = name_re.match(line)

		if new_match is not None:
			new_name = line.split("Title:")[1].strip()
			return new_name
		return None

	@staticmethod
	def extract_incipit(line):
		name_re = re.compile(r"Incipit: (.*)")
		new_match = name_re.match(line)

		if new_match is not None:
			new_name = line.split("Incipit:")[1].strip()
			return new_name
		return None

	@staticmethod
	def extract_key(line):
		name_re = re.compile(r"Key: (.*)")
		new_match = name_re.match(line)

		if new_match is not None:
			new_name = line.split("Key:")[1].strip()
			return new_name
		return None

	@staticmethod
	def extract_genre(line):
		name_re = re.compile(r"Genre: (.*)")
		new_match = name_re.match(line)

		if new_match is not None:
			new_name = line.split("Genre:")[1].strip()
			return new_name
		return None

	@staticmethod
	def extract_year(line):
		com_year_re = re.compile(r"Composition Year: (.*)")
		new_match = com_year_re.match(line)

		if new_match is not None:
			new_year = line.split("Composition Year:")[1].strip()

			year = re.findall(r"\d{4}", new_year)

			if len(year) > 0:
				return int(year[0].strip())

		return None


class Voice:
	def __init__(self, name, range):
		self.name = name
		self.range = range

	@staticmethod
	def extract_voice(line):
		voice_re = re.compile(r"Voice \d+:")
		new_match = voice_re.match(line)

		if new_match is not None:
			line = re.sub(voice_re, "Voice:", line)
			voice_info = line.split("Voice:")[1].strip()

			if "--" in voice_info:
				voice_info = voice_info.replace(",", ";", 1)
				voice_info = voice_info.split(";")
				if len(voice_info) > 1:
					voice_range = voice_info[0].strip()
					voice_name = voice_info[1].strip()
				else:
					voice_range = voice_info[0].strip()
					voice_name = None
			else:
				voice_name = voice_info.strip()
				voice_range = None

			new_voice = Voice(voice_name, voice_range)
			return new_voice


class Person:
	def __init__(self, name, born, died):
		self.name = name
		self.born = born
		self.died = died

	@staticmethod
	def extract_composers(line):
		com_re = re.compile(r"Composer: (.*)")
		new_match = com_re.match(line)

		composers_list = []
		if new_match is not None:
			composers = line.split("Composer:")[1].split(";")

			for composer in composers:

				if Person.number_in_string(composer):
					com_info = composer.split(" (")
					com_name = com_info[0].strip()

					if len(com_info) > 1:
						if Person.plus_in_string(com_info[1]):
							com_born = None
							com_died = int(com_info[1].split("+")[1].replace(")", "")[0:4].strip())
						else:
							years = com_info[1].replace("--", "-")
							if len(years.split("-")[0].strip()) > 0:
								com_born = int(years.split("-")[0][0:4].strip())
							else:
								com_born = None

							if len(years.split("-")[1].replace(")", "").strip()) > 0:
								com_died = int(years.split("-")[1].replace(")", "")[0:4].strip())
							else:
								com_died = None

				else:
					com_name = composer.strip()
					com_born = None
					com_died = None

				new_person = Person(com_name, com_born, com_died)
				composers_list.append(new_person)
		return composers_list

	@staticmethod
	def extract_editors(line):
		editors_re = re.compile(r"Editor: (.*)")
		new_match = editors_re.match(line)

		editors_list = []

		if new_match is not None:
			editors = line.split("Editor:")[1].strip()

			whole_names_re = re.compile(r"\w+ \w+")
			whole_names_match = whole_names_re.match(editors)

			if whole_names_match is not None:
				if ',' in editors:
					editors = editors.split(",")
				else:
					editors = [editors]
			else:
				if ',' in editors:
					editors = editors.split(",")
					editors = [",".join(i) for i in zip(editors[::2], editors[1::2])]
				else:
					editors = [editors]

			for editor in editors:
				new_person = Person(editor.strip(), None, None)
				editors_list.append(new_person)

		return editors_list

	@staticmethod
	def number_in_string(s):
		return any(i.isdigit() for i in s)

	@staticmethod
	def plus_in_string(s):
		return "+" in s


def open_file(filename):
	# fix opening on win - set encoding
	try:
		f = open(filename, 'r', encoding="utf8")
		return f
	except Exception as e:
		print(e)
		return


def parse_sections(filename):
	sections = filename.read().split("\n\n")

	if len(sections) > 0:
		return sections

	print("No print sections in file.")
	return


def load(filename):
	prints_list = []

	f = open_file(filename)
	sections = parse_sections(f)

	for section in sections:
		if not section:
			continue

		section_lines = section.split("\n")

		print_id = None
		composition_name = None
		composition_incipit = None
		composition_key = None
		composition_genre = None
		composition_year = None
		voices = []
		composers = []
		edition_name = None
		editors = []
		print_id = None
		partiture = None

		for s_line in section_lines:
			s_line = s_line.strip()
			if "Print Number:" in s_line:
				print_id = Print.extract_id(s_line)
			elif "Partiture:" in s_line:
				partiture = Print.extract_partiture(s_line)
			elif "Edition:" in s_line:
				edition_name = Edition.extract_name(s_line)
			elif "Composer:" in s_line:
				composers = Person.extract_composers(s_line)
			elif "Title:" in s_line:
				composition_name = Composition.extract_name(s_line)
			elif "Incipit:" in s_line:
				composition_incipit = Composition.extract_incipit(s_line)
			elif "Key:" in s_line:
				composition_key = Composition.extract_key(s_line)
			elif "Genre:" in s_line:
				composition_genre = Composition.extract_genre(s_line)
			elif "Composition Year:" in s_line:
				composition_year = Composition.extract_year(s_line)
			elif "Voice" in s_line:
				new_voice = Voice.extract_voice(s_line)
				voices.append(new_voice)
			elif "Editor:" in s_line:
				editors = Person.extract_editors(s_line)
			else:
				continue

		new_composition = Composition(composition_name, composition_incipit, composition_key, composition_genre, composition_year, voices, composers)
		new_edition = Edition(new_composition, editors, edition_name)
		new_print = Print(new_edition, print_id, partiture)

		prints_list.append(new_print)

	return prints_list

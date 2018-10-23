import re
import sys
from collections import Counter


def open_file():
    # fix opening on win - set encoding
    try:
        f = open(sys.argv[1], 'r', encoding="utf8")
    except Exception as e:
        print(e)
        try:
            f = open(sys.argv[1], 'r')
        except Exception as e:
            print(e)

    return f


def get_composers_stats():
    counter = Counter()
    p = re.compile("Composer: (.*)")

    f = open_file()

    for line in f:
        new_match = p.match(line)

        if new_match is not None:
            composers = line.split(":")[1].split(";")

            for composer in composers:
                composer = re.sub("([(\[]).*?([)\]])", "", composer).strip()
                if len(composer) > 0:
                    counter[composer] += 1

    for item, value in counter.items():
        print(item.strip() + ": " + str(value))


def get_centuries_stats():
    counter = Counter()
    p = re.compile("Composition Year: (.*)")

    f = open_file()

    for line in f:
        new_match = p.match(line)

        if new_match is not None:
            year = line.split(":")[1].strip()
            if len(year) > 0:
                year = re.findall(r'\d{4}|\d{2}(?=th)', year)
                if len(year[0]) > 2:
                    counter[year[0][:2]] += 1
                else:
                    year[0] = int(year[0]) - 1
                    counter[str(year[0])] += 1

    for item, value in counter.items():
        item = int(item) + 1
        print(str(item).strip() + "th century: " + str(value))


parameter = sys.argv[2]

if parameter == "composer":
    get_composers_stats()
elif parameter == "century":
    get_centuries_stats()
else:
    print("Invalid parameter given.")

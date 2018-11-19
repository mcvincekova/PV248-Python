import pandas
import sys
import json


def group_and_remove(data_table, mode):
	if mode == "dates":
		data_table = data_table.rename(lambda column: column[:10], axis="columns")
		# print(data_table)
	elif mode == "exercises":
		data_table = data_table.rename(lambda column: column[-2:], axis="columns")
	elif mode == "deadlines":
		return data_table
	else:
		return None
	# https://pandas.pydata.org/pandas-docs/version/0.18/groupby.html
	data_table = data_table.groupby(level=0, axis=1).sum()

	return data_table


def generate_output(data_table):
	output = {}

	for column in data_table:
		column_output = {"mean": data_table[column].mean(), "median": data_table[column].median(),
		                 "first": data_table[column].quantile(0.25), "last": data_table[column].quantile(0.75),
		                 "passed": count_passed(data_table[column])}
		output[column] = column_output

	return output


def count_passed(points):
	result = 0
	for p in points:
		if p > 0:
			result += 1

	return result


def run():
	f = sys.argv[1]
	mode = sys.argv[2]

	data_table = pandas.read_csv(f, header=0, index_col="student")
	data_table = group_and_remove(data_table, mode)

	output = generate_output(data_table)
	print(json.dumps(output, indent=2, ensure_ascii=False))


run()

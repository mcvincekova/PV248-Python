import pandas
import sys
import json


def group_and_remove(f, split_param):

	data_table = pandas.read_csv(f, header=0, index_col="student")
	if split_param == "dates":
		data_table = data_table.rename(lambda column: column[:10], axis="columns")
	elif split_param == "exercises":
		data_table = data_table.rename(lambda column: column[-2:], axis="columns")
	else:
		return None
	# https://pandas.pydata.org/pandas-docs/version/0.18/groupby.html
	data_table = data_table.groupby(level=0, axis=1).sum()

	return data_table


def get_values(data_table, student_id):

	output = []

	if student_id == "average":
		for column in data_table:
			average = data_table[column].mean()
			output.append(average)
	else:
		extract = data_table.loc[int(student_id)]
		for item in extract:
			output.append(item)

	return output


def run():
	f = sys.argv[1]
	# student id or average
	student_id = sys.argv[2]

	data_table = group_and_remove(f, split_param="exercises")
	ex_points = get_values(data_table, student_id)
	print(ex_points)

	data_table = group_and_remove(f, split_param="dates")
	date_points = get_values(data_table, student_id)
	print(date_points)


run()

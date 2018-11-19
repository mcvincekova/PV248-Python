import sys
import pandas
from numpy import cumsum, median, mean
from datetime import datetime
from scipy.stats import linregress
from math import ceil
import json


def group_and_remove(f, split_param):

	data_table = pandas.read_csv(f, header=0, index_col="student")

	# strip white spaces for "%Y-%m-%d" compatibility
	if split_param == "dates":
		data_table = data_table.rename(lambda column: column.strip()[:10], axis="columns")
	elif split_param == "exercises":
		data_table = data_table.rename(lambda column: column.strip()[-2:], axis="columns")
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


def get_reg_slope(data_table, date_points):
	dates = []
	for date in data_table.columns.values:
		date = datetime.strptime(date, "%Y-%m-%d")
		dates.append(date)

	dates_sorted = sorted(dates)

	dates_numeric = []
	for date in dates_sorted:
		date = datetime.toordinal(date)
		dates_numeric.append(date)

	cumulative_points = cumsum(date_points)
	slope, intercept, r_value, p_value, std_deviation = linregress(dates_numeric, cumulative_points)

	day_sixteen = (datetime.strptime("2018-09-17", "%Y-%m-%d") + pandas.Timedelta(days=(16.0 / slope))).strftime("%Y-%m-%d")
	day_twenty = (datetime.strptime("2018-09-17", "%Y-%m-%d") + pandas.Timedelta(days=(20.0 / slope))).strftime("%Y-%m-%d")

	return slope, day_sixteen, day_twenty


def generate_output(points, slope, d_sixteen, d_twenty):
	output = {"mean": mean(points), "median": median(points), "passed": count_passed(points), "total": sum(points),
	          "slope": slope, "date 16": d_sixteen, "date 20": d_twenty}

	return output


def count_passed(points):
	result = 0
	for p in points:
		if p > 0:
			result += 1

	return result


def run():
	f = sys.argv[1]
	# student id or average
	student_id = sys.argv[2]

	data_table = group_and_remove(f, split_param="exercises")
	ex_points = get_values(data_table, student_id)

	data_table = group_and_remove(f, split_param="dates")
	date_points = get_values(data_table, student_id)

	reg_slope, day_sixteen, day_twenty = get_reg_slope(data_table, date_points)

	output = generate_output(ex_points, reg_slope, day_sixteen, day_twenty)
	print(json.dumps(output, indent=2, ensure_ascii=False))


run()

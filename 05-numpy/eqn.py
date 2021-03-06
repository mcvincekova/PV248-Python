from numpy import linalg
import sys
import re
import copy


def open_file(filename):
	# fix opening on win - set encoding
	try:
		f = open(filename, 'r', encoding="utf8")
	except Exception as e:
		print(e)
		try:
			f = open(filename, 'r')
		except Exception as e:
			print(e)

	return f


def parse_line(line):
	line = line.replace(" ", "")
	tokens = re.findall(r"[+|-]*[0-9]*[a-z]", line)

	eq_dict = {}
	for token in tokens:
		variable = re.findall(r"[a-z]+", token)
		value = re.findall(r'\d*\.?\d+', token)

		if "-" in token:
			if len(value) != 0:
				eq_dict[variable[0]] = -float(value[0])
			else:
				eq_dict[variable[0]] = - 1.0
		else:
			if len(value) != 0:
				eq_dict[variable[0]] = float(value[0])
			else:
				eq_dict[variable[0]] = 1.0

	return eq_dict


def find_all_variables(line):
	found_variables = set()
	reg = re.compile(r"[a-z]")
	for char in line:
		if reg.match(char):
			found_variables.add(char)

	return found_variables


def format_solution(variables, solution):
	print("solution: ", end=" ")

	output = []
	variables.sort()
	for i in range(len(variables)):
		single_output = str(variables[i]) + " = " + str(solution[i])
		output.append(single_output)

	print(', '.join(output))


def run():

	eq_file = open_file(sys.argv[1])

	results = []
	full_left_sides = []

	for line in eq_file:
		split_eq_sides = line.split("=")
		full_left_sides.append(split_eq_sides[0].strip())
		results.append(float(split_eq_sides[1].replace(" ", "")))

	# Find all variables used in the equation system
	all_variables = set()
	for item in full_left_sides:
		all_variables.update(find_all_variables(item))

	equations = []
	for item in full_left_sides:
		line_result = parse_line(item)
		for variable in all_variables:
			# If variable is not in the given equation add 0.0 coefficient
			if variable not in line_result.keys():
				line_result[variable] = 0.0

		# Sort the coefficient with respect to the variables
		line_result = sorted(line_result.items())
		sorted_dict = {}
		for element in line_result:
			sorted_dict[element[0]] = element[1]

		equations.append(sorted_dict)

	# Get the coefficients
	left_sides_coefficients_matrix = []
	for equation in equations:
		left_sides_coefficients_matrix.append(list(equation.values()))

	# Create the augmented matrix
	left_to_append = copy.deepcopy(left_sides_coefficients_matrix)
	rights_to_append = copy.deepcopy(results)

	augmented = []
	for i in range(len(left_to_append)):
		left_to_append[i].append(rights_to_append[i])
		augmented.append(left_to_append[i])

	# Check for an existing solution
	# ... any system of linear equations is inconsistent (has no solutions)
	# if the rank of the augmented matrix is greater than the rank of the coefficient matrix ...
	if linalg.matrix_rank(augmented) == linalg.matrix_rank(left_sides_coefficients_matrix):
		# Check for the unique solution
		# ... The solution is unique if and only if the rank equals the number of variables ...
		if linalg.matrix_rank(left_sides_coefficients_matrix) == len(all_variables):
			solution = linalg.solve(left_sides_coefficients_matrix, results)
			format_solution(list(all_variables), solution)
		else:
			# ... The general solution has k free parameters
			# where k is the difference between the number of variables and the rank ...
			space_dimension = len(all_variables) - linalg.matrix_rank(left_sides_coefficients_matrix)
			print("solution space dimension: " + str(space_dimension))
	else:
		print("no solution")

run()

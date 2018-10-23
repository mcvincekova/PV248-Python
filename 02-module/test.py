import scorelib
import sys

for print_instance in scorelib.load(sys.argv[1]):
	print_instance.format()


#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
import os
import itertools

def run(combination):
	marker_names = list(map(lambda x: os.path.basename(os.path.dirname(x)), combination))
	dir_name = '_'.join(marker_names)
	combo_str = ' '.join(combination)
	py_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
						   "ensemble.py")
	print("echo", ' '.join(marker_names))
	print("mkdir", dir_name)
	print("cd", dir_name)
	print("python3", py_file, combo_str, '> output.txt')
	print("cd ..")
#	out_name =
if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s dir_name" % sys.argv[0])
		sys.exit(1)
	elif not os.path.isdir(sys.argv[1]):
		print(sys.argv[1], "must be a directory")
	marker_types = [os.path.join(sys.argv[1], d) for d in os.listdir(sys.argv[1])]
	dir_list = list(filter(os.path.isdir, marker_types))
	dir_list = list(map(lambda x: os.path.abspath(os.path.join(x, "m_max")), dir_list))
	dir_list = list(filter(os.path.isdir, dir_list))
	print("#!/usr/bin/env bash")
	for L in range(1, len(dir_list)):
		for combo in itertools.combinations(dir_list, L):
			run(combo)

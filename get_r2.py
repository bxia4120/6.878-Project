from ensemble import read_output
import sys
from scipy.stats import linregress
import os

def gather_prediction(name):
	if os.path.isfile(name):
		return read_output(name)
	elif not os.path.isdir(name):
		print(name, "is not a file or directory")
	pred_files = [os.path.join(os.path.abspath(name), x) for x in os.listdir(name) if x[:4] == "pred"]
	P = []
	L = []
	for f in pred_files:
		p, l = read_output(f)
		P += p
		L += l
	return P, L

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s dirname" % sys.argv[0])
		sys.exit(1)
	P, L = gather_prediction(sys.argv[1])
	slope, intercept, r_value, p_value, std_err = linregress(L, P)
	print(r_value)

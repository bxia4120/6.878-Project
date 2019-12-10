#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
import pickle

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s model.pickle" % sys.argv[0])
		sys.exit(1)
	with open(sys.argv[1], 'rb') as F:
		data = pickle.load(F)
	if 'regressor' in data.named_steps:
		c = data.named_steps['regressor'].coef_
		S = list(map(str, list(c)))
		print("\t".join(S))

	elif 'classifier' in data.named_steps:
		c = data.named_steps['classifier'].coef_
		for row in c:
			S = list(map(str, list(row)))
			print("\t".join(S))
	elif 'multiclass' in data.named_steps:
		c = data.named_steps['multiclass'].coef_
		for row in c:
			S = list(map(str, list(row)))
			print("\t".join(S))
		#

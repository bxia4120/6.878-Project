#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
from pr_curve import gather_prediction
import numpy as np
from loader import Loader

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s dirname" % sys.argv[0])
		sys.exit(1)
	P, L = gather_prediction(sys.argv[1])
	labels = set([Loader._age_bin(l) for l in L])
	for lab in labels:
		predictions = [p for p, l in zip(P, L) if Loader._age_bin(l) == lab]
		abs_err = np.abs([p - np.mean(lab) for p in predictions])
		print(lab, len(predictions), "%.3f" % np.mean(abs_err), "%.3f" % np.std(abs_err))

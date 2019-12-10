#!/usr/bin/env python3
# Author: Benjamin T. James
import sys, os
import pickle
from loader import Loader
import numpy as np
import pandas as pd

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("Usage: %s dir1 dir2 ..." % sys.argv[0])
		sys.exit(1)

	total = {}
	for arg in sys.argv[1:]:
		fname = os.path.join(arg, "data.pickle")
		if os.path.isfile(fname):
			with open(fname, 'rb') as F:
				data = pickle.load(F)
				labels = data['scaler'].inverse_transform(data['labels']).flatten()
				bins = [Loader._age_bin(l) for l in labels]
				bin_set = sorted(list(set(bins)))
				total[arg] = {b: bins.count(b) for b in bin_set}
	all_keys = []
	for bv in total.values():
		for k in bv.keys():
			if k not in all_keys:
				all_keys.append(k)
	all_keys = sorted(all_keys)
	all_markers = sorted(list(total.keys()))
	arr = np.zeros((len(total.keys()), len(all_keys)))
	for marker, bins in total.items():
		for b, count in bins.items():
			i = all_markers.index(marker)
			j = all_keys.index(b)
			arr[i, j] = count

	final_keys = ["%d - %d" % (int(m[0]), int(m[1])) for m in all_keys]
	df = pd.DataFrame(data=arr.astype(int), columns=final_keys, index=all_markers)
	print(df.to_latex())

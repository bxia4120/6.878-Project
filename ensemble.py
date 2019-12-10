#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
import os
import numpy as np
from loader import Loader
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from kernel import Unscaler
def read_output(filename):
	P = []
	L = []
	with open(filename, 'r') as F:
		for rline in F:
			line = list(map(float, rline.strip().split()))
			P.append(line[0])
			L.append(line[1])
	return (P, L)

def dist(index_list, lab_list_list):
	vals = [L[i][1] for L, i in zip(lab_list_list, index_list)]
	M = np.mean(vals)
	# mse
	return np.mean([(v - M) * (v - M) for v in vals])

def get_pairings(lab_list_list):
	# get all possible distances
	indices = [[i] for i in range(len(lab_list_list[0]))]
	for L in lab_list_list[1:]:
		indices = [I + [j] for j in range(len(L)) for I in indices]
	scores = [dist(I, lab_list_list) for I in indices]
	I = np.argsort(scores)[:min([len(v) for v in lab_list_list])]
	return [indices[idx] for idx in I]

def run(P, L, crossval=3):
	crossval = min(len(P), crossval)
	scaler = MinMaxScaler()
	Ld = [[l] for l in L]
	L_t = scaler.fit_transform(Ld)
	scorer = Unscaler(scaler, get_weights=lambda x: x.named_steps['regressor'].coef_).rscorer
	model = Pipeline([("regressor", LinearRegression())])
	scores = cross_val_score(model,
							 scaler.transform(P),
							 L_t,
							 cv=crossval,
							 n_jobs=1,
							 scoring=scorer)
	out = np.asarray(scores)
	print("all mae:", np.abs(out))
	print("mae: %.2f +/- %.2f" % (np.abs(np.mean(out)), np.std(out)))

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print("Usage: %s dir1 dir2 ..." % sys.argv[0])
		sys.exit(1)
	dir_list = sys.argv[1:]
	tbl = {}
	for d in dir_list:
		if not os.path.isdir(d):
			print("\"%s\" is not a directory" % d)
			sys.exit(1)
		flist = [os.path.join(d, i) for i in os.listdir(d) if i[:4] == 'pred']
		P = []
		L = []
		for f in flist:
			p, l = read_output(f)
			P += p
			L += l
		bins = [Loader._age_bin(a) for a in L]
		for p, l, b in zip(P, L, bins):
			# order by label group
			if b not in tbl:
				tbl[b] = {}
			if d not in tbl[b]:
				tbl[b][d] = []
			tbl[b][d].append((p, l))
	P = []
	L = []
	for b, T in tbl.items():
		d_names = sorted(list(T.keys()))
		if len(d_names) != len(dir_list):
			continue
		# find closest pairings without replacement
		d_vals = [T[d] for d in d_names] # T[d] are each a list of (p, l)
		pairings = get_pairings(d_vals)

		for tup in pairings: # returns L x len(d_names
			p = [d[t][0] for d, t in zip(d_vals, tup)]
			l = [d[t][1] for d, t in zip(d_vals, tup)]
			P.append(p)
			L.append(np.mean(l))
	run(P, L)

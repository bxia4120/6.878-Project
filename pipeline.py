#!/usr/bin/env python3
import sys, os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.pipeline import Pipeline
from data import Data
from kernel import PolyKernel

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s bin_size" % sys.argv[0])
		sys.exit(1)
	if os.path.isfile(sys.argv[1]):
		data = Data(sys.argv[1])
	else:
		bin_size = int(sys.argv[1])
		data = Data(bin_size=bin_size, chrom_sizes={"chr1": 249250621})#, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895, "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753, "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr2": 243199373, "chr20": 63025520, "chr21": 48129895, "chr22": 51304566, "chr3": 198022430, "chr4": 191154276, "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022, "chr9": 141213431, "chrX": 155270560, "chrY": 59373566})#{"chr2": 243199373})
		data.dump("data.pickle")
		# poly(X) = (X^T * X / len(X) + c0)^d
	X_train, X_test, y_train, y_test = train_test_split(
		data.feature_list, data.label_list.flatten(), test_size=0.33, random_state=42)

	print(np.asarray(X_train).shape, np.asarray(y_train).shape)
	print(np.asarray(X_test).shape, np.asarray(y_test).shape)
	lr = LinearRegression()
	model = Pipeline([("kernel", PolyKernel()),
					  ("regressor", lr)])
	model.fit(X_train, y_train)
	predicted = model.predict(X_test)
	s_pred = data.scaler.inverse_transform([[p] for p in predicted])
	s_y    = data.scaler.inverse_transform([[y] for y in y_test])
	for a, b in zip(s_pred, s_y):
		print(a, b)
	with open('weights.txt', 'w') as F:
		print(' '.join(list(map(str, lr.coef_))), file=F)
	print("mae:", np.mean([np.abs(a - b) for a, b in zip(s_pred, s_y)]))

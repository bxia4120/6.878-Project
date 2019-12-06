#!/usr/bin/env python3
import sys, os
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import ElasticNet, LinearRegression, SGDRegressor, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from data import Data
from kernel import PolyKernel, Unscaler
import numpy as np
from util import *

np.seterr(divide='ignore', invalid='ignore')

def reshape_data(model_data, op=np.add):
	n_markers = model_data.shape[1]
	if n_markers == 1:
		return model_data.reshape((model_data.shape[0],
								   model_data.shape[2]))
	return op(*[model_data[:, i, :] for i in range(n_markers)])

def run(model_data, crossval=10, n_feat=1000, mode="r"):
	print("Data:", model_data.feature_list.shape)
	print("Labels:", model_data.label_list.flatten().shape)
	mod_list = []

	Lab = model_data.label_list.flatten()
	if mode == "c":
		Lab[Lab >= 0.5] = 1
		Lab[Lab <  0.5] = 0
		scorer = None
		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_classif, k=n_feat)))
		mod_list.append(("classifier", LogisticRegression()))
	elif mode == "r":
		scorer = Unscaler(model_data.scaler).rscorer
		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_regression, k=n_feat)))
		mod_list.append(("regressor", LinearRegression()))
	elif mode == 'm':
		Lab, onehot_labels = Unscaler(model_data.scaler).multiclass_onehot(model_data.label_list)
		scorer = Unscaler(model_data.scaler, data=onehot_labels).mscorer
		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_regression, k=n_feat)))
		mod_list.append(("multiclass", LogisticRegression()))
	else:

		print("Mode \"%s\" not implemented" % mode)
		sys.exit(1)
	model = Pipeline(mod_list)
	scores = cross_val_score(model, reshape_data(model_data.feature_list),
							 Lab, cv=crossval,
							 n_jobs=1,
							 scoring=scorer)
	out = np.asarray(scores)
	print("all mae:", np.abs(out))
	print("mae: %.2f +/- %.2f" % (np.abs(np.mean(out)), np.std(out)))
	# with open('weights.txt', 'w') as F:
	# 	print(' '.join(list(map(str, lr.coef_))), file=F)

if __name__ == "__main__":
	args = get_args()

	chrom_sizes={"chr1": 249250621, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895, "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753, "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr2": 243199373, "chr20": 63025520, "chr21": 48129895, "chr22": 51304566, "chr3": 198022430, "chr4": 191154276, "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022, "chr9": 141213431}
	if args['pickle']:
		data = Data(filename=args['pickle'],
					chrom_sizes=chrom_sizes,
					balance=args['balance'])
	else:
		data = Data(bin_size=10000,
					chrom_sizes=chrom_sizes,
					balance=args['balance'],
					marker_list=args['marker'])
		data.dump("data.pickle")
	run(data, mode=args['type'], n_feat=args['num_feat'])

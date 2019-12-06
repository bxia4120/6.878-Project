#!/usr/bin/env python3
import sys, os
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import ElasticNet, LinearRegression, SGDRegressor
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from data import Data
from kernel import PolyKernel, Unscaler
import numpy as np

np.seterr(divide='ignore', invalid='ignore')

def reshape_data(model_data, op=np.add):
	n_markers = model_data.shape[1]
	if n_markers == 1:
		return model_data.reshape((model_data.shape[0],
								   model_data.shape[2]))
	return op(*[model_data[:, i, :] for i in range(n_markers)])


def run(model_data, crossval=10, n_feat=1000):
	print("Data:", model_data.feature_list.shape)
	print("Labels:", model_data.label_list.flatten().shape)
	model = Pipeline([
#		("feat_select", SelectKBest(f_regression, k=n_feat)),
#		("poly_kernel", PolynomialFeatures(degree=2)),
		("regressor", LinearRegression())
	])
	scores = cross_val_score(model, reshape_data(model_data.feature_list),
							 model_data.label_list.flatten(), cv=crossval,
							 n_jobs=1,
							 scoring=Unscaler(model_data.scaler).scorer)
	out = np.asarray(scores)
	print("all mae:", np.abs(out))
	print("mae: %.2f +/- %.2f" % (np.abs(np.mean(out)), np.std(out)))
	# with open('weights.txt', 'w') as F:
	# 	print(' '.join(list(map(str, lr.coef_))), file=F)

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s bin_size" % sys.argv[0])
		sys.exit(1)
	chrom_sizes={"chr1": 249250621, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895, "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753, "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr2": 243199373, "chr20": 63025520, "chr21": 48129895, "chr22": 51304566, "chr3": 198022430, "chr4": 191154276, "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022, "chr9": 141213431, "chrX": 155270560}#{"chr2": 243199373})
	if os.path.isfile(sys.argv[1]):
		data = Data(filename=sys.argv[1], chrom_sizes=chrom_sizes)
	else:
		bin_size = int(sys.argv[1])
		data = Data(bin_size=bin_size,
					chrom_sizes=chrom_sizes,
					marker_list=['H3K27ac'])
		data.dump("data.pickle")
	run(data)

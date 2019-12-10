#!/usr/bin/env python3
import sys, os
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import ElasticNet, LinearRegression, SGDRegressor, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
from sklearn.decomposition import PCA
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from data import Data
from kernel import PolyKernel, Unscaler
import numpy as np
from util import *
from matplotlib import rc
rc('text', usetex=True)

np.seterr(divide='ignore', invalid='ignore')

#best_indices=[972,148873,149616,94280,114623]
best_indices = []
def reshape_data(model_data, op=np.add):
	n_markers = model_data.shape[1]
	if n_markers == 1:
		M = model_data.reshape((model_data.shape[0],
								model_data.shape[2]))
		if len(best_indices) > 0:
			return M[:,best_indices]
		return M
	return op(*[model_data[:, i, :] for i in range(n_markers)])

def run(model_data, crossval=3, n_feat=1000, mode="r", kernel=None, model_type="lr", extra=None):
	print("Data:", model_data.feature_list.shape)
	print("Labels:", model_data.label_list.flatten().shape)
	mod_list = []

	Lab = model_data.label_list.flatten()
	if mode == "c":
		Lab[Lab >= 0.5] = 1
		Lab[Lab <  0.5] = 0
		scorer = Unscaler(model_data.scaler,
						  get_weights=lambda x: x.named_steps['classifier'].coef_).cscorer

		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_classif, k=n_feat)))
		mod_list.append(("classifier", LogisticRegression()))
	elif mode == "r":
		gw = None
		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_regression, k=n_feat)))
		if model_type == "lr":
			mod_list.append(("regressor", LinearRegression()))
			gw = lambda x: x.named_steps['regressor'].coef_
		elif model_type == 'svm':
			degree = 3
			if extra:
				degree = extra
			mod_list.append(("regressor", SVR(kernel='poly', degree=degree)))
			gw = lambda x: x.named_steps['regressor'].dual_coef_
		elif model_type == 'mlp':
			size = 10
			if extra:
				size = extra
			mod_list.append(("regressor", MLPRegressor(hidden_layer_sizes=(size,))))
			gw = lambda x: x.named_steps['regressor'].coefs_
		elif model_type == 'rf':
			num = 100
			if extra:
				num = extra
			mod_list.append(("regressor", RandomForestRegressor(n_estimators=num)))
			gw = lambda x: [[0.123456789]]
		else:
			print("Bad model type", model_type)
			sys.exit(1)
		scorer = Unscaler(model_data.scaler,
						  get_weights=gw).rscorer

	elif mode == 'm':
		Lab, onehot_labels = Unscaler(model_data.scaler).multiclass_onehot(model_data.label_list)
		print(Lab.shape)
		scorer = Unscaler(model_data.scaler,
						  get_weights=lambda x: x.named_steps['multiclass'].coef_,
						  data=onehot_labels,
						  ).mscorer
		if n_feat > 0:
			mod_list.append(("feat_select", SelectKBest(f_regression, k=n_feat)))
		mod_list.append(("multiclass", LogisticRegression(multi_class='multinomial', solver='newton-cg')))
	else:

		print("Mode \"%s\" not implemented" % mode)
		sys.exit(1)
	if kernel and kernel > 0 and n_feat > 1:
		# need feature selection if poly kernel is feasible
		pk = PolynomialFeatures(degree=kernel)
		mod_list.append(("poly", pk))
	model = Pipeline(mod_list)
	scores = cross_val_score(model, reshape_data(model_data.feature_list),
							 Lab,
							 cv=KFold(n_splits=crossval, shuffle=True),
							 n_jobs=1,
							 scoring=scorer)
	out = np.asarray(scores)
	print("all mae:", np.abs(out))
	print("mae: %.2f +/- %.2f" % (np.abs(np.mean(out)), np.std(out)))
	# with open('weights.txt', 'w') as F:
	# 	print(' '.join(list(map(str, lr.coef_))), file=F)

if __name__ == "__main__":
	args = get_args()
	print("wd:", os.getcwd())
	print("sys.args:", sys.argv[1:])
	chrom_sizes={"chr1": 249250621, "chr10": 135534747, "chr11": 135006516, "chr12": 133851895, "chr13": 115169878, "chr14": 107349540, "chr15": 102531392, "chr16": 90354753, "chr17": 81195210, "chr18": 78077248, "chr19": 59128983, "chr2": 243199373, "chr20": 63025520, "chr21": 48129895, "chr22": 51304566, "chr3": 198022430, "chr4": 191154276, "chr5": 180915260, "chr6": 171115067, "chr7": 159138663, "chr8": 146364022, "chr9": 141213431}
	print("Args:", args)
	if args['pickle']:
		data = Data(filename=args['pickle'],
					chrom_sizes=chrom_sizes,
					metadata_file=args['json'],
					balance=args['balance'])
	else:
		data = Data(bin_size=10000,
					data_dir=args['data'],
					chrom_sizes=chrom_sizes,
					metadata_file=args['json'],
					balance=args['balance'],
					marker_list=args['marker'])
		data.dump("data.pickle")
	run(data, mode=args['type'], n_feat=args['num_feat'], kernel=args['kernel'], model_type=args['regressor'], extra=args['extra'])

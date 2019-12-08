from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.metrics import accuracy_score, mean_absolute_error
import pickle
from loader import Loader

class PolyKernel(BaseEstimator, TransformerMixin):
	def transform(self, pdata):
		"""pdata is ENTIRE data set NS x NF"""
		out = []
		for r_x in pdata:
			x = r_x
			pk = polynomial_kernel(x.reshape(-1, 1)).flatten()
			out.append(np.concatenate((x, pk), axis=None))
		return np.asarray(out)

	def fit(self, data, target):
		return self

def dump_prediction(Pred, Label, filename="out.txt"):
	with open(filename, 'w') as F:
		for p, l in zip(Pred, Label):
			print(p, l, file=F)
def dump_weights(coef_list, filename):
	with open(filename, 'w') as F:
		for p in coef_list:
			print(p, file=F)
def dump_feat_select(kbest, filename):
	with open(filename, 'w') as F:
		for s in kbest.get_support(True):
			print(s, file=F)

def dump_model(model, filename):
	with open(filename, 'wb') as F:
		pickle.dump(model, F)

class Unscaler(BaseEstimator, TransformerMixin):
	def __init__(self, scaler, data=None, get_weights=lambda x: x.coef_):
		self.scaler = scaler
		self.counter = 1
		self.get_weights = get_weights
		self.data = data
	def fit(self, data, target):
		return self
	def transform(self, data):
		return self.scaler.inverse_transform(data)

	def cscorer(self, estimator, X, y):
		pred_y = estimator.predict(X)
		pred_y[pred_y >= 0.5] = 1
		pred_y[pred_y < 0.5] = 0
		dump_prediction(pred_y.flatten(), y.flatten(), filename="pred%d.txt" % self.counter)
		dump_weights(self.get_weights(estimator), filename="weights%d.txt" % self.counter)
		dump_model(estimator, filename="model%d.pickle" % self.counter)
		if 'feat_select' in estimator.named_steps:
			dump_feat_select(estimator.named_steps['feat_select'], filename="feat%d.txt" % self.counter)

		self.counter += 1
		return accuracy_score(y.flatten(), pred_y.flatten())

	def rscorer(self, estimator, X, y):
		"""to do: get key in estimator to feat_select and dump
ie "feat_select" in vars(estimator.byname)
		"""
		pred_y = estimator.predict(X)
		self.get_weights = lambda x: x.named_steps['regressor'].coef_
		pred_y[pred_y > 1] = 1
		pred_y[pred_y < 0] = 0
		t_pred_y = self.scaler.inverse_transform(pred_y.reshape(-1, 1))
		t_y = self.scaler.inverse_transform(y.reshape(-1, 1))
		dump_prediction(t_pred_y.flatten(), t_y.flatten(), filename="pred%d.txt" % self.counter)
		dump_weights(self.get_weights(estimator), filename="weights%d.txt" % self.counter)
		dump_model(estimator, filename="model%d.pickle" % self.counter)
		if 'feat_select' in estimator.named_steps:
			dump_feat_select(estimator.named_steps['feat_select'], filename="feat%d.txt" % self.counter)
		self.counter += 1
		return -1 * mean_absolute_error(t_y.flatten(), t_pred_y.flatten())

	def mscorer(self, estimator, X, y):
		pred_y = estimator.predict(X)
		onehot_labels = self.data # I -> bin
		pred_age = []
		actual_age = []#self.scaler.inverse_transform(y.reshape(-1, 1)).flatten()
		for pred in pred_y:
			age = np.mean(onehot_labels[pred])
#			age = np.mean(onehot_labels[np.argmax(pred)])
			pred_age.append(age)
		for ac in y:
			age = np.mean(onehot_labels[ac])
			actual_age.append(age)
		dump_prediction(pred_age, actual_age, filename="pred%d.txt" % self.counter)
		dump_weights(self.get_weights(estimator), filename="weights%d.txt" % self.counter)
		dump_model(estimator, filename="model%d.pickle" % self.counter)
		if 'feat_select' in estimator.named_steps:
			dump_feat_select(estimator.named_steps['feat_select'], filename="feat%d.txt" % self.counter)
		self.counter += 1
		return -1 * mean_absolute_error(actual_age, pred_age)

	def multiclass_onehot(self, L):
		bins = [Loader._age_bin(age) for age in self.scaler.inverse_transform(L).flatten()]
		bin_hash = {b: i for i, b in enumerate(list(set(bins)))}
		bin_indices = [bin_hash[b] for b in bins]
		return np.asarray(bin_indices), {i: b for b, i in bin_hash.items()}
		# onehot = np.eye(len(bin_hash))[bin_indices]
		# return onehot, {i: b for b, i in bin_hash.items()}

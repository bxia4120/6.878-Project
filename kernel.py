from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from sklearn.metrics import accuracy_score, mean_absolute_error

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
		dump_prediction(pred_y.flatten(), y.flatten(), filename="out%d.txt" % self.counter)
		dump_weights(self.get_weights(estimator), filename="weights%d.txt" % self.counter)
		self.counter += 1
		return accuracy_score(y.flatten(), pred_y.flatten())

	def rscorer(self, estimator, X, y):
		"""to do: get key in estimator to feat_select and dump"""
		pred_y = estimator.predict(X)
		pred_y[pred_y > 1] = 1
		pred_y[pred_y < 0] = 0
		t_pred_y = self.scaler.inverse_transform(pred_y.reshape(-1, 1))
		t_y = self.scaler.inverse_transform(y.reshape(-1, 1))
		dump_prediction(t_pred_y.flatten(), t_y.flatten(), filename="out%d.txt" % self.counter)
		dump_weights(self.get_weights(estimator), filename="weights%d.txt" % self.counter)
		self.counter += 1
		return -1 * mean_absolute_error(t_y.flatten(), t_pred_y.flatten())
	def mscorer(self, estimator, X, y):
		pred_y = estimator.predict(X)
		onehot_labels = self.data # I -> bin

	def multiclass_onehot(self, L):
		bins = [Loader._age_bin() for age in self.scaler.inverse_transform(L).flatten()]
		bin_hash = {b: i for i, b in enumerate(list(set(bins)))}
		bin_indices = [bin_hash[b] for b in bins]
		onehot = np.eye(len(bin_hash))[bin_indices]
		return onehot, {i: b for b, i in bin_hash.items()}

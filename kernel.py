from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
import numpy as np

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

class Unscaler(BaseEstimator, TransformerMixin):
	def __init__(self, scaler):
		self.scaler = scaler
		self.counter = 1
	def fit(self, data, target):
		return self
	def transform(self, data):
		return self.scaler.inverse_transform(data)
	def scorer(self, estimator, X, y):
		pred_y = estimator.predict(X)
		pred_y[pred_y > 1] = 1
		pred_y[pred_y < 0] = 0
		t_pred_y = self.scaler.inverse_transform(pred_y.reshape(-1, 1))
		t_y = self.scaler.inverse_transform(y.reshape(-1, 1))
		dump_prediction(t_pred_y.flatten(), t_y.flatten(), filename="out%d.txt" % self.counter)
		self.counter += 1
		return -1 * np.mean(np.abs([(a - b) for a, b in zip(t_pred_y, t_y)]))

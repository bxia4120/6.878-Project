from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class PolyKernel(BaseEstimator, TransformerMixin):
	def transform(self, pdata):
		"""pdata is ENTIRE data set NS x NF"""
		out = []
		for x in pdata:
			pk = polynomial_kernel(x.reshape(-1, 1)).flatten()
			print("shape:", x.shape, pk.shape)
			out.append(np.concatenate((x, pk), axis=None))
		return np.asarray(out)

	def fit(self, data, target):
		return self

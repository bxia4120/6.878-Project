from sklearn.metrics.pairwise import polynomial_kernel
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class PolyKernel(BaseEstimator, TransformerMixin):
	def transform(self, pdata):
		"""pdata is ENTIRE data set NS x NF"""
		out = []
		for r_x in pdata:
			x = r_x * 2
			pk = polynomial_kernel(x.astype(np.uint8).reshape(-1, 1)).flatten() * 2
			print("shape:", x.shape, pk.shape)
			out.append(np.concatenate((x.astype(np.uint8), pk), axis=None))
		return np.asarray(out)

	def fit(self, data, target):
		return self

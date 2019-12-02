import pickle
from loader import Loader
from bin import Binner
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import polynomial_kernel
import os

class Data:
	def __init__(self, filename=None,
				 bin_size=10000, metadata_file='metadata.json',
				 chrom_sizes=None):
		if filename:
			with open(filename, 'rb') as P:
				data = pickle.load(P)
				self.feature_list = data['features']
				self.label_list = data['labels']
				self.scaler = data['scaler']
				self.chrom_sizes = data['chrom_sizes']
				self.bin_size = data['bin_size']
				self.indices = data['indices']
		else:
			if not chrom_sizes or type(chrom_sizes) is not dict:
				raise ValueError("chrom size table not passed")
			if not os.path.isfile(metadata_file):
				raise ValueError("%s is not a file" % metadata_file)
			self.indices, self.feature_list, self.label_list, self.scaler = self._get_data(bin_size, metadata_file, chrom_sizes)
			self.chrom_sizes = chrom_sizes
			self.bin_size = bin_size

	def dump(self, filename):
		tbl = {"features": self.feature_list,
			   "labels": self.label_list,
			   "scaler": self.scaler,
			   "chrom_sizes": self.chrom_sizes,
			   "indices": self.indices,
			   "bin_size": self.bin_size
		}
		with open(filename, 'wb') as P:
			pickle.dump(tbl, P)

	def append_poly_kernel(self):
		print("init shape:", self.feature_list.shape)
		poly_k = polynomial_kernel(self.feature_list)
		print("poly k shape:", poly_k.shape)
		print("flattened poly k shape:", poly_k.flatten().shape)

	def _get_data(self, bin_size, metadata_file, chrom_sizes):
		ldr = Loader("metadata.json")
		bnr = Binner(chrom_sizes, bin_size)
		raw_label_list = []
		raw_feature_list = []
		for label, v_list in ldr.table.items():
			print("label:", label, len(v_list[0]))
			for (actual_age_list, filename) in v_list:
				print("fname:", filename)
				try:
					bw = pyBigWig.open(filename)
					F = bnr.featurize(bw)
					raw_feature_list.append(F)
					raw_label_list.append(actual_age_list)
					file.close()
				except:
					pass
		avg_label_list = np.asarray([[np.mean(y)] for y in raw_label_list])
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		z_feature_list = np.asarray(raw_feature_list)
		nz_feature_list = np.nonzero(z_feature_list)
		indices = sorted(list(set(nz_feature_list[1])))
		return indices, z_feature_list[:, indices], labels, scaler

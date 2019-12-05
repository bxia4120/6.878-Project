import pickle
from loader import Loader
from bin import Binner
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import polynomial_kernel
import os
import pyBigWig

class Data:
	def __init__(self, marker_list, filename=None,
				 bin_size=10000, metadata_file='metadata.json', # or {h3k27ac: ac_metadata.json, ...}
				 chrom_sizes=None):
		if filename:
			with open(filename, 'rb') as P:
				data = pickle.load(P)
				self.feature_list = data['features']
				self.label_list = data['labels']
				self.scaler = data['scaler']
				self.chrom_sizes = data['chrom_sizes']
				self.bin_size = data['bin_size']
		elif type(metadata_file) is str:
			if not chrom_sizes or type(chrom_sizes) is not dict:
				raise ValueError("chrom size table not passed")
			if not os.path.isfile(metadata_file):
				raise ValueError("%s is not a file" % metadata_file)
			self.feature_list, self.label_list, self.scaler = self._get_data(bin_size, metadata_file, marker_list, chrom_sizes)
			self.chrom_sizes = chrom_sizes
			self.bin_size = bin_size
		else:
			raise ValueError("Must provide pickle file or metadata file and marker list")
	def dump(self, filename):
		tbl = {"features": self.feature_list,
			   "labels": self.label_list,
			   "scaler": self.scaler,
			   "chrom_sizes": self.chrom_sizes,
			   "bin_size": self.bin_size
		}
		with open(filename, 'wb') as P:
			pickle.dump(tbl, P)

	def _get_data(self, bin_size, metadata_file, marker_list, chrom_sizes):
		ldr = Loader(metadata_file, marker_list)
		bnr = Binner(chrom_sizes, bin_size)
		raw_label_list = []
		raw_feature_list = []
		label_list = sorted([len(v_list) for lab, v_list in ldr.table.items()])
		print("label list:", label_list)
		min_val = label_list[len(label_list) * 4 // 5] # bottom 80%

		print("min=", min_val)
		for label, v_list in ldr.table.items():
			print("label:", label, len(v_list))
			for (actual_age_list, filename_dict) in v_list[:min(len(v_list), min_val)]:
				datum = []
				for marker in marker_list:
					file_list = filename_dict[marker]
					filename = file_list[0]	 # TODO: can we use multiple?
					print("fname:", filename)
					try:
						bw = pyBigWig.open(filename)
						F = bnr.featurize(bw)
						bw.close()
						datum.append(F)
					except Exception as e:
						print("bad fname:", filename, ":", e)
						pass
				if len(datum) == len(marker_list):
					raw_feature_list.append(datum)
					raw_label_list.append(actual_age_list)
		avg_label_list = np.asarray([[np.mean(y)] for y in raw_label_list])
		print(avg_label_list.flatten())
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		z_feature_list = np.asarray(raw_feature_list)
		# nz_feature_list = np.nonzero(z_feature_list)
		# indices = sorted(list(set(nz_feature_list[1:])))
		return z_feature_list, labels, scaler

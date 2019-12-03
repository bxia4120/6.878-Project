import pickle
from loader import Loader, Metaloader
from bin import Binner
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import polynomial_kernel
import os
import pyBigWig

class Data:
	def __init__(self, filename=None,
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
				self.indices = data['indices']
		elif type(metadata_file) is str:
			if not chrom_sizes or type(chrom_sizes) is not dict:
				raise ValueError("chrom size table not passed")
			if not os.path.isfile(metadata_file):
				raise ValueError("%s is not a file" % metadata_file)
			self.indices, self.feature_list, self.label_list, self.scaler = self._get_data(bin_size, metadata_file, chrom_sizes)
			self.chrom_sizes = chrom_sizes
			self.bin_size = bin_size
		elif type(metadata_file) is dict:
			if not chrom_sizes or type(chrom_sizes) is not dict:
				raise ValueError("chrom size table not passed")
			self.feature_list, self.label_list, self.scaler = self._get_meta_data(bin_size, metadata_file, chrom_sizes)
			self.chrom_sizes = chrom_sizes
			self.bin_size = bin_size
			self.indices = list(range(len(self.feature_list)))

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

	def _get_meta_data(self, bin_size, metadata_marker2file_dict, chrom_sizes):
		marker_list = sorted(list(metadata_marker2file_dict.keys()))
		metafile_list = [metadata_marker2file_dict[M] for M in marker_list]
		dir_list = ["Blood/%s/data" % M for M in marker_list]
		ldr = Metaloader(metafile_list, marker_list, dir_list)
		bnr = Binner(chrom_sizes, bin_size)
		file_data, raw_labels = ldr.get_data()
		data = []
		for f_list in file_data:
			# in same order as marker_list, passed to Metaloader
			datum = []
			for f in f_list:
				try:
					bw = pyBigWig.open(f)
					F = bnr.featurize(bw)
					datum.append(F)
					bw.close()
				except Exception as e:
					print("bad fname:", f, ":", e)
					pass
			data.append(np.asarray(datum))
		avg_label_list = [[x] for x in raw_labels]
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		z_feature_list = np.asarray(data)
		return z_feature_list, labels, scaler

	def _get_data(self, bin_size, metadata_file, chrom_sizes):
		ldr = Loader(metadata_file)
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
					bw.close()
				except Exception as e:
					print("bad fname:", filename, ":", e)
					pass
		avg_label_list = np.asarray([[np.mean(y)] for y in raw_label_list])
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		z_feature_list = np.asarray(raw_feature_list)
		nz_feature_list = np.nonzero(z_feature_list)
		indices = sorted(list(set(nz_feature_list[1:])))
		return indices, z_feature_list[:, indices], labels, scaler

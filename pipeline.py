#!/usr/bin/env python3
import sys,os
from loader import Loader
from bin import Binner
import pyBigWig

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.preprocessing import MinMaxScaler
import pickle

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
		else:
			if not chrom_sizes or type(chrom_sizes) is not dict:
				raise ValueError("chrom size table not passed")
			if not os.path.isfile(metadata_file):
				raise ValueError("%s is not a file" % metadata_file)
			self.feature_list, self.label_list, self.scaler = self._get_data(bin_size, metadata_file, chrom_sizes)

	def dump(self, filename):
		tbl = {"features": self.feature_list,
			   "labels": self.label_list,
			   "scaler": self.scaler}
		with open(filename, 'wb') as P:
			pickle.dump(tbl, P)

	def _get_data(self, bin_size, metadata_file, chrom_sizes):
		ldr = Loader("metadata.json")
		bnr = Binner({'chr2': 243199373}, bin_size)
		raw_label_list = []
		feature_list = []
		for label, v_list in ldr.table.items():
			print("label:", label, len(v_list[0]))
			for (actual_age_list, filename) in v_list:
				print("fname:", filename)
				try:
					bw = pyBigWig.open(filename)
					F = bnr.featurize(bw)
					feature_list.append(F)
					raw_label_list.append(label)
					file.close()
				except:
					pass
		avg_label_list = np.asarray([[np.mean(y)] for y in raw_label_list])
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		return feature_list, labels, scaler


if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s bin_size" % sys.argv[0])
		sys.exit(1)
	if os.path.isfile(sys.argv[1]):
		data = Data(sys.argv[1])
	else:
		bin_size = int(sys.argv[1])
		data = Data(bin_size=bin_size, chrom_sizes={"chr2": 243199373})
		data.dump("data.pickle")
	X_train, X_test, y_train, y_test = train_test_split(
		data.feature_list, data.label_list.flatten(), test_size=0.33, random_state=42)

	print(np.asarray(X_train).shape, np.asarray(y_train).shape)
	print(np.asarray(X_test).shape, np.asarray(y_test).shape)

	model = LinearRegression()
	model.fit(X_train, y_train)
	predicted = model.predict(X_test)
	s_pred = data.scaler.inverse_transform([[p] for p in predicted])
	s_y    = data.scaler.inverse_transform([[y] for y in y_test])
	for a, b in zip(s_pred, s_y):
		print(a, b)
	print("mae:", np.mean([np.abs(a - b) for a, b in zip(s_pred, s_y)]))

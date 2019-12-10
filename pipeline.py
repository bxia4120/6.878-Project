#!/usr/bin/env python3
import json,sys,os
from loader import Loader
from bin import Binner
import pyBigWig

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import *
from sklearn.preprocessing import MinMaxScaler
import pickle

class Data:
	def __init__(self, filename=None,
				 bin_size=10000, metadata_file='metadata.json',
				 chrom_sizes=None, marks=['H3K27ac'], chromosomes=['2']):
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
			self.feature_list, self.label_list, self.scaler = self._get_data(bin_size, metadata_file, chrom_sizes, marks)

	def dump(self, filename):
		tbl = {"features": self.feature_list,
			   "labels": self.label_list,
			   "scaler": self.scaler}
		with open(filename, 'wb') as P:
			pickle.dump(tbl, P)

	def _get_data(self, bin_size, metadata_file, chrom_sizes, marks):
		ldr = Loader(metadata_file, "H3K27ac", "/".join(metadata_file.split("/")[:-1]) + "/data")
		bnr = Binner(chrom_sizes, bin_size)
		raw_label_list = []
		feature_list = []
		for label, v_list in ldr.table.items():
			#print("label:", label, len(v_list[0]))
			for (actual_age_list, filename) in v_list:
				#print("fname:", filename)
				try:
					bw = pyBigWig.open(filename)
					F = bnr.featurize(bw)
					feature_list.append(F)
					raw_label_list.append(actual_age_list)
					file.close()
				except:
					pass
		avg_label_list = np.asarray([[np.mean(y)] for y in raw_label_list])
		scaler = MinMaxScaler()
		scaler.fit(avg_label_list)
		labels = scaler.transform(avg_label_list)
		return feature_list, labels, scaler


if __name__ == "__main__":
	### USAGE: python3 pipeline.py "PATH/TO/METADATA/JSON" "BIN_SIZE" "MARKS,COMMA,SEPARATED" "CHROMOSOMES,COMMA,SEPARATED" ###
	models = {"ard": ARDRegression(), "en": ElasticNet(), "l": Lasso(), "lr": LinearRegression(), "r": Ridge()}
	chrom_sizes = json.load(open("chrom_sizes.json"))
	if len(sys.argv) == 3:
		data = Data(sys.argv[1])
		model_type = models[sys.argv[2]]
	elif len(sys.argv) != 6:
		print("Usage: python3 pipeline.py 'PATH/TO/METADATA/JSON' 'BIN_SIZE' 'MARKS,COMMA,SEPARATED' 'CHROMOSOMES,COMMA,SEPARATED' 'MODEL_TYPE'\n")
		print("python3 pipeline.py 'PATH/TO/PICKLE/' 'MODEL_TYPE'")
		sys.exit(1)
	else:
		metadata_path = sys.argv[1]
		bin_size = int(sys.argv[2])
		markers = sys.argv[3].split(",")
		chromosomes = sys.argv[4].split(",")
		mod_chrom_sizes = {}
		for chromosome in chromosomes:
			chrom_name = 'chr' + chromosome
			mod_chrom_sizes[chrom_name] = chrom_sizes[chrom_name]
		model_type = models[sys.argv[5]]
		data = Data(bin_size=bin_size, metadata_file = metadata_path, chrom_sizes=mod_chrom_sizes)
		data.dump("data.pickle")
	X_train, X_test, y_train, y_test = train_test_split(
		data.feature_list, data.label_list.flatten(), test_size=0.33, random_state=42)

	#print(np.asarray(X_train).shape, np.asarray(y_train).shape)
	#print(np.asarray(X_test).shape, np.asarray(y_test).shape)

	model = model_type
	model.fit(X_train, y_train)
	predicted = model.predict(X_test)
	s_pred = data.scaler.inverse_transform([[p] for p in predicted])
	s_y    = data.scaler.inverse_transform([[y] for y in y_test])
	#for a, b in zip(s_pred, s_y):
		#print(a, b)
	#print("mae:", np.mean([np.abs(a - b) for a, b in zip(s_pred, s_y)]))
	print(np.mean([np.abs(a - b) for a, b in zip(s_pred, s_y)]))

	coeffs = [str(val) for val in model.coef_]
	with open("raw_coeffs.tsv", "w") as out:
		out.write('\t'.join(coeffs))

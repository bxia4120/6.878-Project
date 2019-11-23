#!/usr/bin/env python3
import json
import os
import re
import numpy as np

class Loader:
	def __init__(self, metadata_file, marker='H3K27ac', data_dir="data"):
		with open(metadata_file, 'r') as F:
			self.metadata = json.load(F)
		self.marker = marker
		self.data_dir = data_dir

		healthy_synonyms = set(['none', 'normal', 'healthy', 'presumed_normal'])
		self.table = {}
		for sample_id, sample_info in self.metadata['samples'].items():
			if sample_info.get('disease', 'absent').lower() in healthy_synonyms:
				age = self.get_age(sample_info)
				if age:
					age_bin = self.get_age_bin(np.mean(age))
					val = (age, self.get_filename(sample_id))
					self.table.setdefault(age_bin, []).append(val)

	def get_age_bin(self, age, bin_size=5):
		age_min = age - (age % bin_size)
		age_max = age_min + bin_size - 1
		return (age_min, age_max)

	def get_age(self, sample_info):
		"""returns list of ages gathered from metadata"""
		if 'donor_age' not in sample_info:
			return None
		age = str(sample_info['donor_age'])
		if age == 'NA':
			return None
		R = re.findall('\d+', age)
		if not R:
			return None
		return list(map(int, R))

	def get_filename(self, sample_id):
		S = sample_id + "_" + self.marker
		if not os.path.exists(self.data_dir):
			os.mkdir(self.data_dir)
		if S not in self.metadata['datasets']:
			return None
		out = []
		for sample_data in self.metadata['datasets'][S]['browser']['peak_calls']:
			bname = os.path.basename(sample_data['big_data_url'])
			full_name = os.path.join(self.data_dir, bname)
			if not os.path.exists(full_name):
				os.system('wget ' + sample_data['big_data_url'] + ' --no-check-certificate -P %s' % self.data_dir)
			out.append(full_name)
		return out



if __name__ == "__main__":
	ldr = Loader("metadata.json")
	print(ldr.table)

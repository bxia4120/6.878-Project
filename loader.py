import json
import numpy as np
import os
import re

class Loader:
	"""version 2"""
	def __init__(self, metadata_file, marker_list, bin_size=5):
		with open(metadata_file, 'r') as MF:
			self.metadata = json.load(MF)
		self.marker_list = marker_list
		self.table = {}
		self.bin_size = bin_size

		healthy_synonyms = ['none', 'normal', 'healthy', 'presumed_normal']
		for sample_id, sample_info in self.metadata['samples'].items():
			if sample_info.get('disease', 'absent').lower() in healthy_synonyms:
				self.add_sample(sample_id, sample_info)

	def add_sample(self, sample_id, sample_info):
		age = self.get_age(sample_info)
		if not age:
			return
		age_bin = self.get_age_bin(np.mean(age))
		f_name_list = {}
		for M in self.marker_list:
			L = self.get_filename(sample_id, M)
			if L is None or len(L) == 0 or None in L:
				return
			f_name_list[M] = L
		val = (age, f_name_list)
		self.table.setdefault(age_bin, []).append(val)

	def balance(self):
		age_bins = {k: len(v) for k, v in self.table.items()}
		print(age_bins)

	def get_age_bin(self, age):
		age_min = age - (age % self.bin_size)
		age_max = age_min + self.bin_size - 1
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

	def get_filename(self, sample_id, marker):
		S = sample_id + "_" + marker
		if S not in self.metadata['datasets']:
			return None
		data_dict = self.metadata['datasets'][S]["ihec_data_portal"]
		data_dir_paths = [data_dict['cell_type_category'].replace(' ', '_'),
						  data_dict['cell_type'].replace(' ', '_'),
						  data_dict['assay']]
		data_dir = ""
		for dname in data_dir_paths:
			data_dir = os.path.join(data_dir, dname)
			if not os.path.exists(data_dir):
				os.mkdir(data_dir)
		out = []
		for sample_data in self.metadata['datasets'][S]['browser']['signal_unstranded']:
			bname = os.path.basename(sample_data['big_data_url'])
			full_name = os.path.join(data_dir, bname)
			if not os.path.exists(full_name):
				os.system('wget \'' + sample_data['big_data_url'] + '\' --no-check-certificate -P %s' % data_dir)
			if os.path.isfile(full_name):
				out.append(full_name)
		return out

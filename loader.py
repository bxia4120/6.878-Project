#!/usr/bin/env python3
import json
import os
import re
import numpy as np

class Metaloader:
	def __init__(self, metadata_file_list, marker_list, dir_list):
		self.metadata_list = []
		for f in metadata_file_list:
			with open(f, 'r') as F:
				self.metadata_list.append(json.load(F))
		self.marker_list = marker_list
		self.dir_list = dir_list
		healthy_synonyms = set(['none', 'normal', 'healthy', 'presumed_normal'])
		sample_list = list()
		for metadata in self.metadata_list:
			inner_list = set()
			for sample_key, sample_info in metadata['samples'].items():
				if 'donor_id' in sample_info:
					sample_id = sample_info['donor_id']
					inner_list.add(sample_id)
			sample_list += list(inner_list)
		self.loader_list = []
		for metadata, marker, data_dir in zip(self.metadata_list, marker_list, dir_list):
			table = {}
			for sample_key, sample_info in metadata['samples'].items():
				if 'donor_id' in sample_info:
					sample_id = sample_info['donor_id']
					if sample_list.count(sample_id) == len(self.metadata_list):
						table[sample_key] = sample_info
			ldr = Loader(marker=marker, data_dir=data_dir, metadata=table)
			self.loader_list.append(ldr)

	def get_data(self):
		table = {}
		for ldr, marker in zip(self.loader_list, self.marker_list):
			for donor_id, val in ldr.dtable.items():
				# sets each only once
				table.setdefault(donor_id, {})[marker] = np.mean(val)
		labels = []
		data = []
		for donor_id, marker_table in table.items():
			age_list = [v[0] for k, v in marker_table.items()]
			assert np.max(age_list) == np.min(age_list)
			labels.append(np.mean(age_list))
			datum = [marker_table[M][1] for M in self.marker_list]
			data.append(datum)
		return data, labels

class Loader:
	def __init__(self, metadata_file=None, marker='H3K27ac', data_dir="data", metadata=None):
		if metadata is not None:
			self.metadata = metadata
		elif metadata_file is not None:
			with open(metadata_file, 'r') as F:
				self.metadata = json.load(F)
		else:
			raise ValueError("must provide metadata or metadata file")
		self.marker = marker
		self.data_dir = data_dir

		healthy_synonyms = set(['none', 'normal', 'healthy', 'presumed_normal'])
		self.table = {}
		self.dtable = {}
		for sample_id, sample_info in self.metadata['samples'].items():
			if sample_info.get('disease', 'absent').lower() in healthy_synonyms:
				age = self.get_age(sample_info)
				if not age:
					continue
				age_bin = self.get_age_bin(np.mean(age))
				f_name_list = self.get_filename(sample_id)
				if not f_name_list:
					continue
				for f_name in f_name_list:
					val = (age, f_name)
					if val[1]:
						self.table.setdefault(age_bin, []).append(val)
						if 'donor_id' in sample_info:
							self.dtable.setdefault(sample_info['donor_id'], []).append(val)

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

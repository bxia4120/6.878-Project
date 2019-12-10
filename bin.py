#!/usr/bin/env python3
import pyBigWig
import numpy as np
import json, glob
import sys

class Binner:
	def __init__(self, chrom_sizes, bin_size):
		self.chrom_sizes = chrom_sizes
		self.bin_size = bin_size
		self.num_bins = {}
		self.offset = {}
		self.total_n_bins = 0
		self.chrom_list = sorted(list(self.chrom_sizes.keys()))
		for chrom_name in self.chrom_list:
			n_bases = self.chrom_sizes[chrom_name]
			n_bins = int(np.ceil(n_bases / bin_size))
			self.offset[chrom_name] = self.total_n_bins
			self.num_bins[chrom_name] = n_bins
			self.total_n_bins += n_bins

	def unbin(self, num):
		actual_num = num * self.bin_size
		for chrom_name in self.chrom_list:
			ofst = self.offset[chrom_name]
			if num >= ofst and (num - ofst) < self.num_bins[chrom_name]:
				print("true", chrom_name)
				internal_bin = num - ofst
				return (chrom_name, internal_bin * self.bin_size, (internal_bin + 1) * self.bin_size)
		return None
	def get_bin(self, chrom, position):
		off = position // self.bin_size
		return self.offset[chrom] + off
	def featurize_bed(self, opened_bed_file, col=7):
		"""order:
		chrom  start    end      size   num_data  min   max     mean   sum
		"""
		arr = np.zeros((self.total_n_bins, ))
		last_chr = ''
		last_end = '0'
		idx = 0
		for rline in opened_bed_file:
			line = rline.strip().split()
			if last_chr == '':
				assert line[3] == "%d" % self.bin_size
			if line[0] == last_chr and last_end == line[1]:
				idx += 1
			elif line[0] in self.chrom_sizes.keys():
				idx = self.get_bin(line[0], (int(line[1]) + int(line[2])) // 2)
			else:
				continue
			if line[col] != 'NA' and idx < len(arr):
				arr[idx] = float(line[col])
			last_chr = line[0]
			last_end = line[2]
		return arr
	def featurize(self, opened_file, keep=lambda x: True):
		arr = np.zeros((self.total_n_bins, ))
		for chrom, chrom_len in self.chrom_sizes.items():
			m_len = min(chrom_len, opened_file.chroms()[chrom])
			entries = opened_file.entries(chrom, 0, m_len)
			if not entries:
				continue
			for peak in entries:
				begin = peak[0]
				end = peak[1]
				if keep(peak):
					bin_begin = self.get_bin(chrom, begin)
					bin_end = self.get_bin(chrom, end)
					for i in range(bin_begin, bin_end + 1):
						arr[i] += 1 / len(range(bin_begin, bin_end + 1))
		return arr

if __name__ == "__main__":
	chrom_sizes = json.load(open('chrom_sizes.json'))
	bnr = Binner({'chr2': 100000}, 10000)
	for filename in glob.glob('data/*'):
		try:
			file = pyBigWig.open(filename)
			F = bnr.featurize(file)
			print(F)
			file.close()
		except:
			pass

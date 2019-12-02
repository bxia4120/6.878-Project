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
		for chrom_name in self.chrom_list:
			ofst = self.offset[chrom_name]
			if num >= ofst and num < ofst + self.chrom_sizes[chrom_name]:
				internal_bin = num - ofst
				return (chrom_name, internal_bin * self.bin_size, (internal_bin + 1) * self.bin_size)
		return None
	def get_bin(self, chrom, position):
		off = position // self.bin_size
		return self.offset[chrom] + off

	def featurize(self, opened_file, keep=lambda x: True):
		arr = np.zeros((self.total_n_bins, ))
		for chrom, chrom_len in self.chrom_sizes.items():
			entries = opened_file.entries(chrom, 0, chrom_len)
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

#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

def get_colors(cmap, n=100):
	out = []
	for x in range(n):
		item = cmap(x / n)
		if item not in out:
			out.append(item)
	return out

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s f.tsv" % sys.argv[0])
		sys.exit(1)
	marker_list = []
	data = {}
	model_list = []
	with open(sys.argv[1], 'r') as F:
		for rline in F:
			line = rline.strip().split()
			if line[0] not in marker_list:
				marker_list.append(line[0])
			if line[1] not in model_list:
				model_list.append(line[1])
			data[(line[0], line[1])] = float(line[2])
	arr = np.zeros((len(model_list), len(marker_list)))
	for k, v in data.items():
		(Li, Lj) = k
		i = marker_list.index(Li)
		j = model_list.index(Lj)
		arr[j, i] = v
	vals = arr.tolist()

	ax = plt.subplot(111)
	colors = get_colors(cm.viridis, n=len(model_list))
	offset = 0
	Mo = (1 + len(model_list))
	Ma = len(marker_list)
	x = list(range(0, Ma * Mo, Mo))
	for row, label, color in zip(vals, model_list, colors):

		offset += 1
		ax.bar([z + offset for z in x], row, width=0.75, color=color, align='center', label=label)

#		x += len(vals)
	# ax.bar(x-0.2, y, width=0.2, color=, align='center')
	# ax.bar(x, z, width=0.2, color='g', align='center')
	# ax.bar(x+0.2, k, width=0.2, color='r', align='center')

	plt.legend(model_list)
	plt.xticks([z + Mo / 2 for z in x], marker_list)
	plt.ylabel("Mean absolute error of predicted age")
	plt.savefig("models.png", dpi=500)

#!/usr/bin/env python3
# Author: Benjamin T. James
from pr_curve import read_output
import sys
import numpy as np
from loader import Loader
from matplotlib import cm
import matplotlib.pyplot as plt
from scipy.stats import linregress
import os

def get_colors(cmap, n=100):
	out = []
	for x in range(n):
		item = cmap(x / n)
		if item not in out:
			out.append(item)
	return out

def gather_prediction(name):
	if os.path.isfile(name):
		return read_output(name)
	elif not os.path.isdir(name):
		print(name, "is not a file or directory")
	pred_files = [os.path.join(os.path.abspath(name), x) for x in os.listdir(name) if x[:4] == "pred"]
	P = []
	L = []
	for f in pred_files:
		p, l = read_output(f)
		P += p
		L += l
	return P, L



# boxplot errors ?
# raw values (scatter) with lines for reference
if __name__ == "__main__":
	if len(sys.argv[1:]) != 2:
		print("Usage: %s dirname title" % sys.argv[0])
		sys.exit(1)
	P, L = gather_prediction(sys.argv[1])
	print("unique L:", len(list(set(L))))
	slope, intercept, r_value, p_value, std_err = linregress(L, P)
	mae = np.mean(np.abs([p - l for p, l in zip(P, L)]))
	print("linregress:", slope, intercept, r_value, p_value, std_err)
	labels = sorted(list(set([Loader._age_bin(l) for l in L])))
	colors = get_colors(cm.viridis, n=len(labels))
	for i, lab in enumerate(labels):
		predictions = [p for p, l in zip(P, L) if Loader._age_bin(l) == lab]
		labels = [l for l in L if Loader._age_bin(l) == lab]
		print(predictions)
		y = i / len(labels)
		std = 0.001
		y = [np.mean(lab) for q in predictions] + np.random.randn(len(predictions)) * std
		plt.scatter(labels, predictions, c=[colors[i] for _ in y])
#		plt.axvline(x=np.mean(lab), c=colors[i])
		plt.xlim(0, 80)
		plt.ylim(0, 80)
	axes = plt.gca()
	x_vals = np.array(axes.get_xlim())
	y_vals = intercept + slope * x_vals
	props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
	text = "MAE: %.3f\n" % mae
	text += r"$R^2$: %.3f" % r_value
	plt.text(10, 70, text, horizontalalignment='center',
			 verticalalignment='center', bbox=props)
	plt.xlabel("Actual age")
	plt.ylabel("Predicted age")
	plt.title(sys.argv[2])
	plt.plot(x_vals, y_vals, '--', c='gray', label="fit")
	plt.plot(x_vals, x_vals, '-', c='black')

	plt.savefig("scatter.png")

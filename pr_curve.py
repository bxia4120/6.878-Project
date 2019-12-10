#!/usr/bin/env python3
# Author: Benjamin T. James
import sys
from ensemble import read_output
from sklearn.metrics import precision_recall_curve as pr_curve
import matplotlib.pyplot as plt
import os

def gather_prediction(dirname):
	pred_files = [os.path.join(os.path.abspath(dirname), x) for x in os.listdir(dirname) if x[:4] == "pred"]
	P = []
	L = []
	for f in pred_files:
		p, l = read_output(f)
		P += p
		L += l
	return P, L

def run(dname):
	P, L = gather_prediction(dirname)
	precision, recall, thresholds = pr_curve(L, P)
	plt.figure()
	plt.step(recall, precision, where='post')

	plt.xlabel('Recall')
	plt.ylabel('Precision')
	plt.ylim([0.0, 1.05])
	plt.xlim([0.0, 1.0])
	plt.title(
		'precision-recall curve')
	plt.savefig('out.png')

if __name__ == "__main__":
	if len(sys.argv[1:]) != 1:
		print("Usage: %s dirname" % sys.argv[0])
		sys.exit(1)
	elif not os.path.isdir(sys.argv[1]):
		print(sys.argv[1], "is not a directory")
		sys.exit(1)
	run(os.path.abspath(sys.argv[1]))

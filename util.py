import os, sys
import argparse
import numpy as np
import re

def file_type(x):
	if os.path.isfile(x):
		return x
	return None
def dir_type(x):
	if os.path.isdir(x):
		return x
	return None

def get_args():
	parser = argparse.ArgumentParser(description='prediction model for age from histone modifications')
	parser.add_argument('-p', '--pickle', nargs='?', type=file_type,
                        default=None)
	parser.add_argument('-m', '--marker', nargs='+', type=str, default=[])
	parser.add_argument('-r', '--regressor', nargs='?', type=str, default='lr')
	parser.add_argument('-t', '--type', nargs="?", type=str, default='regression')
	parser.add_argument('-b', '--balance', nargs='?', type=str, default="max")
	parser.add_argument('-n', '--num-feat', nargs='?', type=int, default=-1)
	parser.add_argument('-j', '--json', nargs='?', type=file_type, default=None)
	parser.add_argument('-d', '--data', nargs='?', type=dir_type, default=None)
	parser.add_argument('-k', '--kernel', nargs='?', type=int)
	parser.add_argument('-x', '--extra', nargs='?', type=int)
	args = vars(parser.parse_args())
	if args['type'] in ['regr', 'regression', 'regress']:
		args['type'] = "r"
	elif args['type'] in ['class', 'classification', 'classify']:
		args['type'] = "c"
	elif args['type'] in ['multi', 'multiclass', 'multi-class']:
		args['type'] = 'm'
	else:
		print("Type must be regression, classification, or multi-class")
		sys.exit(1)
	if args['balance'] in ['max', 'maximum']:
		args['balance'] = np.max
	elif args['balance'] in ['min', 'minimum']:
		args['balance'] = np.min
	elif re.match(r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?', args['balance']):
		f = float(args['balance'])
		args['balance'] = lambda x: x[int(len(x) * f)]
	else:
		print("Balance must be either max or min")
		sys.exit(1)
	if args['num_feat'] < 0:
		args['num_feat'] = 0
	return args

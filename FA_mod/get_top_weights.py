import csv, json, math, os, sys

def create_index_list(bin_size):
	index_list = []
	chrom_sizes = json.load(open('../chrom_sizes.json'))
	last_index = 0
	for i in range(1, 23):
		chrom = 'chr' + str(i)
		size = math.ceil(chrom_sizes[chrom] / bin_size)
		for j, k in enumerate(range(last_index, last_index + size)):
			if k == last_index + size - 1:
				index_list.append((i, j * bin_size + 1, chrom_sizes[chrom]))
			else:
				index_list.append((i, j * bin_size + 1, (j + 1) * bin_size))
	return index_list

if len(sys.argv) != 2:
	print('Usage: python3 get_top_weights.py N')
n = int(sys.argv[1])

inp_file = "feat3"

with open(inp_file + '.txt') as inp:
	reader = csv.reader(inp, delimiter = '\t')
	raw_coeffs = next(reader)
for i, val in enumerate(raw_coeffs):
	raw_coeffs[i] = (val, i)
sorted_coeffs = sorted(raw_coeffs, key = lambda x: int(x[0]), reverse = True)


index_list = create_index_list(10000)

with open(inp_file + '.bed', 'w') as out:
	for i in range(n):
		weight_info = index_list[sorted_coeffs[i][1]]
		out.write('chr' + str(weight_info[0]) + '\t' + str(weight_info[1]) + '\t' + str(weight_info[2]) + '\n')
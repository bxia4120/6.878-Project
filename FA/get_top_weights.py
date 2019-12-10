import json, math, os, sys

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

coeff_files = ['H3K27me3_weights.tsv', 'H3K4me3_weights.tsv']
coeff_weights = [0.6337245237525694, 0.6489571308804527]
raw_coeffs = [0 for _ in range(288113)]
for i, coeff_file in enumerate(coeff_files):
	with open(coeff_file) as inp:
		for j, line in enumerate(inp):
			raw_coeffs[j] += coeff_weights[i] * float(line.strip())
		#raw_coeffs = [coeff_weights[i] * float(val) for val in next(reader)]

for i, val in enumerate(raw_coeffs):
	raw_coeffs[i] = (val, i)
sorted_coeffs = sorted(raw_coeffs, key = lambda x: abs(float(x[0])), reverse = True)

index_list = create_index_list(10000)

with open('top_weights.bed', 'w') as out:
	for i in range(n):
		weight_info = index_list[sorted_coeffs[i][1]]
		out.write('chr' + str(weight_info[0]) + '\t' + str(weight_info[1]) + '\t' + str(weight_info[2]) + '\n')
import re

inp_name = 'feat3'

goi = set()
with open(inp_name + '_goi_raw.txt') as inp:
	for line in inp:
		for gene in re.split(',|;', line.split()[3]):
			goi.add(gene)

with open(inp_name + '_goi.txt', 'w') as out:
	for gene in goi:
		out.write(gene + '\n')
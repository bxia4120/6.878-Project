import re

goi = set()
with open('goi_raw.txt') as inp:
	for line in inp:
		for gene in re.split(',|;', line.split()[3]):
			goi.add(gene)

with open('goi.txt', 'w') as out:
	for gene in goi:
		out.write(gene + '\n')
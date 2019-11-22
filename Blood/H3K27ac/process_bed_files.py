import json
import glob
import pyBigWig

chrom_sizes = json.load(open('chrom_sizes.json'))

for filename in glob.glob('./data/*'):
	file = pyBigWig.open(filename)
	print(file.entries('chr1', 0, 100000))
	file.close()
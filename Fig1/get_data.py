import json,os

data = {}
bin_sizes = ['5000', '10000', '50000', '100000']
chromosomes = [str(i) for i in range(1,23)]
os.chdir('..')
for bin_size in bin_sizes:
	data[bin_size] = {}
	for chromosome in chromosomes:
		data[bin_size][chromosome] = os.popen('python3 pipeline.py ./Blood/H3K27ac/metadata.json ' + bin_size + ' H3K27ac ' + chromosome + ' lr').read().strip()
		print('Chromosome ' + str(chromosome) + ' with size ' + str(bin_size) + ' bin done')
with open("data.json", "w") as output:
	json.dump(data, output)
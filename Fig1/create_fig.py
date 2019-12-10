import json
import matplotlib.pyplot as plt
import numpy as np

data = json.load(open('data.json'))

bin_sizes = ['5000', '10000', '50000', '100000']
chromosomes = [str(i) for i in range(1,23)]

bar_width = 0.2

bars = []
for bin_size in bin_sizes:
	bar = []
	for chromosome in chromosomes:
		bar.append(float(data[bin_size][chromosome]))
	bars.append(bar)

rs = [np.arange(len(chromosomes))]
for _ in range(len(chromosomes) - 1):
	rs.append([x + bar_width for x in rs[-1]])

colors = [i * (1 / len(bin_sizes)) for i in range(len(bin_sizes))]

plt.figure(figsize = (15, 5))

for i in range(len(bin_sizes)):
	plt.bar(rs[i], bars[i], color = (colors[i], colors[i], colors[i]), width = bar_width, edgecolor = 'white', label = bin_sizes[i])

plt.xlabel('Chromosome')
plt.ylabel('Mean absolute error (years)')

plt.xticks([r + ((len(bin_sizes) - 1) * bar_width / 2) for r in range(len(chromosomes))], chromosomes)

plt.legend(title = 'Bin size')

plt.tight_layout()

plt.savefig('./fig1.png', dpi = 600)
import numpy as np
import matplotlib.pyplot as plt

labels = ["H3K27ac", "H3K27me3", "H3K4me3", "H3K4me1"]

data = np.array([[12.54,	13.78, 	12.90, 	13.30],
				 [13.78, 	9.80, 	9.04, 	10.26],
				 [12.90,	9.04, 	14.77, 	12.69],
				 [13.30, 	10.26, 	12.69, 	12.78]])

error = np.array([[2.99,	1.64,	2.80,	2.17],
				  [1.64, 	2.16,	2.48,	2.10],
				  [2.80,	2.48,	6.29,	2.68],
				  [2.17,	2.10,	2.68,	3.38]])


fig, ax = plt.subplots()
im = ax.imshow(data, cmap = "Wistia", vmin = 9.04, vmax = 21.99)
fig.colorbar(im, ax = ax)

ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels)
ax.set_yticklabels(labels)
ax.xaxis.tick_top()

plt.setp(ax.get_xticklabels(), rotation=45)

for i in range(len(labels)):
    for j in range(len(labels)):
        text = ax.text(j, i, str(data[i, j]) + " ± " + str(error[i, j]),
                       ha="center", va="center", color="black")

plt.tight_layout()
plt.show()
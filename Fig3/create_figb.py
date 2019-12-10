import numpy as np
import matplotlib.pyplot as plt

labels_one = ["H3K27ac", "H3K27me3"]
labels_two = ["H3K27ac", "H3K4me1"]

data = np.array([[12.00, 12.72],
				 [16.62, 12.09]])

error = np.array([[2.67, 3.75],
				  [2.24, 1.43]])


fig, ax = plt.subplots()
im = ax.imshow(data, cmap = "Wistia", vmin = 9.04, vmax = 21.99)
fig.colorbar(im, ax = ax, pad = 0.2)

ax.tick_params(axis="both", bottom=True, top=True, left=True, right=True, labelbottom=True, labeltop=True, labelleft=True, labelright=True)

ax.set_xticks(np.arange(len(labels_one)))
ax.set_yticks(np.arange(len(labels_two)))
ax.set_xticklabels(labels_one)
ax.set_yticklabels(labels_two)
plt.setp([tick.label1 for tick in ax.xaxis.get_major_ticks()], rotation=45)
plt.setp([tick.label2 for tick in ax.xaxis.get_major_ticks()], rotation=45)

for i in range(len(labels_one)):
    for j in range(len(labels_two)):
        text = ax.text(j, i, str(data[i, j]) + " ± " + str(error[i, j]),
                       ha="center", va="center", color="black")

plt.autoscale()
plt.show()
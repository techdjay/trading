from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

# The x and y data to plot
y = np.array([1,2,17,20,16,3,5,4])
x = np.arange(len(y))

# Threshold above which the line should be red
threshold = 15

# Create line segments: 1--2, 2--17, 17--20, 20--16, 16--3, etc.
segments_x = np.r_[x[0], x[1:-1].repeat(2), x[-1]].reshape(-1, 2)
segments_y = np.r_[y[0], y[1:-1].repeat(2), y[-1]].reshape(-1, 2)

# Assign colors to the line segments
linecolors = ['red' if y_[0] > threshold and y_[1] > threshold else 'blue'
              for y_ in segments_y]

# Stamp x,y coordinates of the segments into the proper format for the
# LineCollection
segments = [(x_, y_) for x_, y_ in (segments_x, segments_y)]

# Create figure
plt.figure()
ax = plt.axes()

# Add a collection of lines
ax.add_collection(LineCollection(segments, colors=linecolors))

# Set x and y limits... sadly this is not done automatically for line
# collections
ax.set_xlim(0, 8)
ax.set_ylim(0, 21)
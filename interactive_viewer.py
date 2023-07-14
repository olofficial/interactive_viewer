import obplib as obp
import jdc #utility package for this guide

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import copy
import matplotlib.style as mplstyle
mplstyle.use(['fast'])
plt.rcParams['figure.dpi'] = 400
from matplotlib.collections import LineCollection

def plotty(lines, line_number, upper_lim):
    fig, ax = plt.subplots()
    x_values = [[copy.copy(lines[i].P1.x), copy.copy(lines[i].P2.x)] for i in range(upper_lim)]
    y_values = [[copy.copy(lines[i].P1.y), copy.copy(lines[i].P2.y)] for i in range(upper_lim)]
    min_lines = max(upper_lim - line_number, 0)
    
    line_segments = [[(x_values[i][0], y_values[i][0]), (x_values[i][1], y_values[i][1])] for i in range(min_lines, upper_lim)]
    
    # Create an array of speed values for each line
    speeds = [lines[i].Speed for i in range(min_lines, upper_lim)]
    
    spot_sizes = [lines[i].bp.spot_size for i in range(min_lines, upper_lim)]
    
    line_collection = LineCollection(line_segments, cmap='Wistia_r', linewidth=2)
    line_collection.set_array(np.array(speeds))
    line_collection.set_linestyle('-')
    
    linewidths = np.array(spot_sizes) * 0.01  # Scale linewidths based on spot_size parameter
    
    line_collection.set_linewidth(linewidths)
    ax = plt.gca()
    ax.add_collection(line_collection)
    ax.set_facecolor('xkcd:black')
    plt.colorbar(line_collection)

    last_x_values = x_values[-1]
    last_y_values = y_values[-1]
    plt.scatter(last_x_values[-1], last_y_values[-1], color='w', marker='*', s=spot_sizes[-1], zorder=10)
    
    plt.autoscale()
    plt.grid(False)
    plt.show()

def interactive_viewer(lines):
    line_number = widgets.IntText(value=len(lines), description='Max Lines:', min=1, max=len(lines))
    widgets.interact(plotty, lines=widgets.fixed(lines), upper_lim=(1, len(lines), 1), line_number=line_number, layout=widgets.Layout(width='50%'), continuous_update=True)
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
import matplotlib.pyplot as plt
import matplotlib as mpl

def bezier_curve(control_points, num_points=100):
    t = np.linspace(0, 1, num_points)
    n = len(control_points) - 1

    curve = np.zeros((num_points, 2))
    for i in range(num_points):
        for j in range(n + 1):
            curve[i] += np.multiply([control_points[j][0], control_points[j][1]], bernstein_polynomial(n, j, t[i]))
    return curve

def binomial_coefficient(n, k):
    return np.math.factorial(n) / (np.math.factorial(k) * np.math.factorial(n - k))

def bernstein_polynomial(n, k, t):
    return binomial_coefficient(n, k) * t**k * (1 - t)**(n - k)

def plotty(lines, show_control_points = False):
    line_number = len(lines)
    upper_lim = len(lines)
    fig, ax = plt.subplots()
    curves = []
    for i in range(len(lines)):
        if type(lines[i]) == obp.Line:
            point_1 = np.array([copy.copy(lines[i].P1.x), copy.copy(lines[i].P1.y)])
            point_2 = np.array([copy.copy(lines[i].P2.x), copy.copy(lines[i].P2.y)])
            control_points = np.array([point_1, point_2])
            curves.append(bezier_curve(control_points, 100))
        elif type(lines[i]) == obp.Curve:
            start_point = [copy.copy(lines[i].P1.x), copy.copy(lines[i].P1.y)]
            point_2 = [copy.copy(lines[i].P2.x), copy.copy(lines[i].P2.y)]
            point_3 = [copy.copy(lines[i].P3.x), copy.copy(lines[i].P3.y)]
            end_point = [copy.copy(lines[i].P4.x), copy.copy(lines[i].P4.y)]
            control_points = np.array([start_point, point_2, point_3, end_point])
            curves.append(bezier_curve(control_points, 100))
    min_lines = max(upper_lim - line_number, 0)

    # Create an array of speed values for each line
    speeds = []
    for i in range(min_lines, upper_lim):
        if type(lines[i]) == obp.Line:
            speeds.append(lines[i].Speed)
        elif type(lines[i]) == obp.Curve:
            speeds.append(lines[i].speed)
    
    spot_sizes = [lines[i].bp.spot_size for i in range(min_lines, upper_lim)]
    
    line_collection = LineCollection(curves, cmap='Wistia_r', linewidth=2)
    line_collection.set_array(np.array(speeds))
    line_collection.set_linestyle('-')
    
    linewidths = np.array(spot_sizes) * 0.01  # Scale linewidths based on spot_size parameter
    
    line_collection.set_linewidth(linewidths)
    ax = plt.gca()
    ax.add_collection(line_collection)
    ax.set_facecolor('xkcd:black')
    plt.colorbar(line_collection)
    last_x_values = curves[-1]
    last_y_values = curves[-1]
    plt.scatter(last_x_values[-1][0], last_y_values[-1][1], color='w', marker='*', s=spot_sizes[-1], zorder=10)
    if show_control_points:
        t = mpl.markers.MarkerStyle(marker='*')
        t._transform = t.get_transform().rotate_deg(180)
        plt.scatter(control_points[:, 0], control_points[:, 1], color='w', marker=t, s=spot_sizes[-1] * 0.5, zorder=12)
    plt.autoscale()
    plt.grid(False)
    plt.axis('equal')
    plt.show()

def interactive_viewer(lines, show_control_points = False):
    line_number = widgets.IntText(value=len(lines), description='Max Lines:', min=1, max=len(lines))
    widgets.interact(plotty, lines=widgets.fixed(lines), show_control_points = widgets.fixed(show_control_points), upper_lim=(1, len(lines), 1), line_number=line_number, layout=widgets.Layout(width='50%'), continuous_update=True)
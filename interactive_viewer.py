import obplib as obp
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import copy
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors
import matplotlib as mpl

mpl.style.use(['fast'])
plt.rcParams['figure.dpi'] = 400

def bezier_curve(control_points, num_points=100):
    """Generate a Bézier curve given control points."""
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

def plotty(lines, upper_lim, line_number, show_control_points=False):
    """Plot lines and curves with color and linewidth variation based on attributes.

    Parameters:
        lines (list): List of line objects.
        upper_lim (int): Upper limit for the number of lines to plot.
        line_number (int): Number of lines to plot.
        show_control_points (bool, optional): Whether to display control points.

    Returns:
        None
    """
    min_lines = max(upper_lim - line_number, 0)
    fig, ax = plt.subplots()
    segment_speeds = []
    segment_spot_sizes = []
    curves = []

    # Dictionaries to handle different line types
    line_types = {
        obp.Line: {'speed_attr': 'Speed', 'point_attrs': ['P1', 'P2']},
        obp.Curve: {'speed_attr': 'speed', 'point_attrs': ['P1', 'P2', 'P3', 'P4']},
        obp.AcceleratingLine: {'speed_attr': ('si', 'sf'), 'point_attrs': ['P1', 'P2']},
        obp.AcceleratingCurve: {'speed_attr': ('si', 'sf'), 'point_attrs': ['P1', 'P2', 'P3', 'P4']},
    }

    for i, line in enumerate(lines):
        if upper_lim >= i >= min_lines:
            line_info = line_types[type(line)]
            speed_attr = line_info['speed_attr']
            point_attrs = line_info['point_attrs']

            if isinstance(line_info, obp.Line) or isinstance(line_info, obp.AcceleratingLine):
                num_segments = 2  # Number of segments for coloring the current line
            else:
                num_segments = 100

            control_points = np.array([
                [copy.copy(getattr(line, point_attr).x), copy.copy(getattr(line, point_attr).y)]
                for point_attr in point_attrs
            ])

            curve = bezier_curve(control_points, num_segments)
            if isinstance(speed_attr, str):
                # Constant speed attribute for the current line
                speeds = np.linspace(getattr(line, speed_attr), getattr(line, speed_attr), num_segments - 1)
            else:
                # Varying speed attribute (e.g., tuple of initial and final speed) for the current line
                speeds = np.linspace(getattr(line, speed_attr[0]), getattr(line, speed_attr[1]), num_segments - 1)

            # Append the speeds and spot_sizes for each segment to their respective lists
            segment_speeds.extend(speeds)

            spot_sizes = np.linspace(line.bp.spot_size, line.bp.spot_size, num_segments - 1)
            segment_spot_sizes.extend(spot_sizes)

            # Combine the curves into segments for the current line and append to the main curves list
            curve_array = np.stack([curve[:-1], curve[1:]], axis=1).reshape(-1, 2, 2)
            curves.append(curve_array)

    # Create the overlapping array view with separate sublists for x and y values
    segments_array = np.concatenate(np.array(curves))

    # Create the LineCollection with variable colors for each segment based on speed
    linewidths = np.array(segment_spot_sizes) * 0.01  # Scale linewidths based on spot_size parameter

    norm = mcolors.Normalize(min(segment_speeds), max(segment_speeds))
    cmap = plt.get_cmap('Wistia') 
    lc = LineCollection(segments_array, cmap=cmap, norm=norm)
    lc.set_array(np.array(segment_speeds))
    lc.set_linewidth(linewidths)

    ax.add_collection(lc)
    ax.set_facecolor('xkcd:black')
    plt.colorbar(lc)

    last_x_values = curves[-1]
    last_y_values = curves[-1]
    plt.scatter(last_x_values[-1][0], last_y_values[-1][1], color='w', marker='*', s=segment_spot_sizes[-1], zorder=10)

    if show_control_points:
        t = mpl.markers.MarkerStyle(marker='*')
        t._transform = t.get_transform().rotate_deg(180)
        plt.scatter(control_points[:, 0], control_points[:, 1], color='w', marker=t, s=segment_spot_sizes[-1] * 0.5, zorder=12)

    plt.autoscale()
    plt.grid(False)
    plt.axis('equal')
    plt.show()

def interactive_viewer(lines, show_control_points = False):
    """Create an interactive viewer for lines and curves.

    Parameters:
        lines (list): List of line objects.
        show_control_points (bool, optional): Whether to display control points.

    Returns:
        None
    """
    line_number = widgets.IntText(value=len(lines), description='Max Lines:', min=1, max=len(lines))
    widgets.interact(plotty, lines=widgets.fixed(lines), show_control_points = widgets.fixed(show_control_points), upper_lim=(1, len(lines), 1), line_number=line_number, layout=widgets.Layout(width='50%'), continuous_update=True)
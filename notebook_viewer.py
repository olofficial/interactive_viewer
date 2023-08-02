import obplib as obp
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import copy
import matplotlib.colors as mcolors
import matplotlib as mpl

mpl.style.use(['fast'])
plt.rcParams['figure.dpi'] = 400

class TimedPoint():
    """Helper class to store timed points."""
    def __init__(self, coords, dwell_time, bp):
        self.coords = coords
        self.dwell_time = dwell_time
        self.bp = bp

# Dictionary to define object types and their attributes
object_types = {
    obp.Line: {'speed_attr': 'Speed', 'point_attrs': ['P1', 'P2']},
    obp.Curve: {'speed_attr': 'speed', 'point_attrs': ['P1', 'P2', 'P3', 'P4']},
    obp.AcceleratingLine: {'speed_attr': ('si', 'sf'), 'point_attrs': ['p1', 'p2']},
    obp.AcceleratingCurve: {'speed_attr': ('si', 'sf'), 'point_attrs': ['P1', 'P2', 'P3', 'P4']},
    obp.TimedPoints: {},
    TimedPoint: {}
}

def unpack_timedpoints(timedpoints):
    """Unpack TimedPoints objects into a list of TimedPoint instances."""
    timedpoints_list = []
    dwell_time_const = False  # Flag to determine if dwell time is constant
    bp = timedpoints.bp
    if timedpoints.dwellTimes[1:] == [0 for _ in range(len(timedpoints.dwellTimes) - 1)]:
        dwell_time_const = True
        dwell_time = timedpoints.dwellTimes[0]
    for i in range(len(timedpoints.points)):
        coords = [timedpoints.points[i].x, timedpoints.points[i].y]
        if not dwell_time_const:
            dwell_time = timedpoints.dwellTimes[i]
        timedpoints_list.append(TimedPoint(coords, dwell_time, bp))
    return timedpoints_list

def expand_objects(objects):
    """Expand objects into a flat list of objects by unpacking TimedPoints."""
    new_objects = []
    for obj in objects:
        obj_info = object_types.get(type(obj))
        if obj_info is None:
            continue  # Skip objects with unknown types
        if isinstance(obj, obp.TimedPoints):
            new_objects.extend(unpack_timedpoints(obj))
        else:
            new_objects.append(obj)
    return new_objects

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
    """Compute the binomial coefficient (n choose k)."""
    return np.math.factorial(n) / (np.math.factorial(k) * np.math.factorial(n - k))

def bernstein_polynomial(n, k, t):
    """Compute the Bernstein polynomial for a given n and k."""
    return binomial_coefficient(n, k) * t**k * (1 - t)**(n - k)

def mscatter(x, y, ax=None, m=None, **kw):
    """Create a scatter plot with custom markers."""
    import matplotlib.markers as mmarkers
    if not ax:
        ax = plt.gca()
    sc = ax.scatter(x, y, **kw)
    if (m is not None) and (len(m) == len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc

def plot_lines_and_points(objects, upper_lim, object_number, show_control_points=False):
    """Plot lines and TimedPoints with color and size variation based on attributes.

    Parameters:
        objects (list): List of objects.
        upper_lim (int): Upper limit for the number of objects to plot.
        object_number (int): Number of objects to plot.
        show_control_points (bool, optional): Whether to display control points.

    Returns:
        None
    """
    fig, ax = plt.subplots()

    start_object_idx = max(upper_lim - object_number, 0)
    end_object_idx = min(upper_lim, len(objects))

    dwell_times_available = any(isinstance(obj, TimedPoint) for obj in objects[start_object_idx:end_object_idx])
    line_speeds_available = any(isinstance(obj, (obp.Line, obp.AcceleratingLine, obp.Curve, obp.AcceleratingCurve)) for obj in objects[start_object_idx:end_object_idx])

    if dwell_times_available:
        cmap_dwell_times = plt.get_cmap('viridis')  # Colormap for TimedPoints' dwellTimes
        dwell_times_norm = None
        dwell_times_values = [obj.dwell_time for obj in objects]  # Collect all dwell time values

        # Check if there is only one unique value for dwell times
        unique_dwell_times = np.unique(dwell_times_values)
        if len(unique_dwell_times) == 1:
            # If there is only one unique value, manually adjust the normalization
            dwell_times_norm = mcolors.Normalize(unique_dwell_times[0] * 0.9, unique_dwell_times[0] * 1.1)
        else:
            dwell_times_norm = mcolors.Normalize(np.min(dwell_times_values), np.max(dwell_times_values))
    if line_speeds_available:
        cmap_line_speeds = plt.get_cmap('Wistia')  # Colormap for line speed/acceleration
        line_speeds_norm = None

    scatter_points_timed = []  # Separate scatter points list for TimedPoints
    scatter_points_line = []  # Separate scatter points list for line objects
    scatter_sizes_timed = []
    scatter_sizes_line = []
    markers_timed = []
    markers_line = []

    scatter_colors_dwell_times = []  # List for TimedPoints' dwellTimes
    scatter_colors_line_speeds = []  # List for line speed/acceleration

    for i in range(start_object_idx, end_object_idx):
        last_object = i == end_object_idx - 1
        obj = objects[i]

        obj_info = object_types.get(type(obj))
        if obj_info is None:
            continue  # Skip objects with unknown types

        if isinstance(obj, TimedPoint):
            scatter_points_timed.append([obj.coords[0], obj.coords[1]])
            if dwell_times_available:
                scatter_colors_dwell_times.append(obj.dwell_time)
            if last_object:
                markers_timed.append('*')
                scatter_sizes_timed.append(obj.bp.spot_size * 0.3)
            else:
                markers_timed.append('o')
                scatter_sizes_timed.append(obj.bp.spot_size * 0.01)
                
        elif isinstance(obj, (obp.Line, obp.AcceleratingLine, obp.Curve, obp.AcceleratingCurve)):
            scatter_params = plot_line(ax, obj, cmap_line_speeds, show_control_points=show_control_points)
            if last_object:
                last_point = scatter_params[0]
                scatter_points_line.append([last_point[1][0], last_point[1][1]])
                scatter_sizes_line.append(scatter_params[1])
                markers_line.append('*')
            if len(scatter_params) > 3:
                for i in range(len(scatter_params[2])):
                    scatter_points_line.append([scatter_params[2][i][0], scatter_params[2][i][1]])
                    scatter_sizes_line.append(scatter_params[1] * 0.3)
                    markers_line.append(scatter_params[2][1])
            scatter_colors_line_speeds.extend(scatter_params[-1])
            
    scatter_points_timed = np.array(scatter_points_timed)
    scatter_points_line = np.array(scatter_points_line)
    
    if dwell_times_available:

        # Check if there is only one unique value for dwell times
        unique_dwell_times = np.unique(dwell_times_values)
        if len(unique_dwell_times) == 1:
            # If there is only one unique value, manually adjust the normalization
            dwell_times_norm = mcolors.Normalize(unique_dwell_times[0] * 0.9, unique_dwell_times[0] * 1.1)
        else:
            dwell_times_norm = mcolors.Normalize(np.min(dwell_times_values), np.max(dwell_times_values))

        last_point_timed = scatter_points_timed[-1]
        # Plot all TimedPoints except the last one with the specified parameters
        
        dwell_times_norm = mcolors.Normalize(np.min(scatter_colors_dwell_times), np.max(scatter_colors_dwell_times))
        dwell_times_cbar = plt.colorbar(plt.cm.ScalarMappable(norm=dwell_times_norm, cmap=cmap_dwell_times), ax=ax)
        dwell_times_cbar.set_label('Dwell Time', rotation=270, labelpad=20)
        plt.scatter(scatter_points_timed[:-1, 0], scatter_points_timed[:-1, 1], c=scatter_colors_dwell_times[:-1], s=scatter_sizes_timed[:-1], marker = 'o', zorder=100)
        plt.scatter(last_point_timed[0], last_point_timed[1], c='white', marker='*', s=scatter_sizes_timed[-1], zorder=101)
    if line_speeds_available:
        last_point_line = scatter_points_line[-1]
        line_speeds_norm = mcolors.Normalize(np.min(scatter_colors_line_speeds), np.max(scatter_colors_line_speeds))
        line_speeds_cbar = plt.colorbar(plt.cm.ScalarMappable(norm=line_speeds_norm, cmap=cmap_line_speeds), ax=ax, label='Speed', location = 'left', ticklocation = 'left')
        # Plot all line objects except the last one with the specified parameters
        if len(scatter_points_line) > 1:
            plt.scatter(scatter_points_line[:-1, 0], scatter_points_line[:-1, 1], c=scatter_colors_line_speeds[:-1], s=scatter_sizes_line[:-1], marker='*', zorder=100)
        # Plot the last line object with different parameters (white star)
        mscatter(last_point_line[0], last_point_line[1], c='white', marker=markers_line[-1], s=scatter_sizes_line[-1], zorder=101)

    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=45, ha='right')
    ax.set_facecolor('xkcd:black')
    ax.set_aspect('equal')

    plt.grid(False)
    plt.show()

def plot_line(ax, line, cmap, show_control_points=False):
    """Plot a line with color and size variation based on attributes."""
    num_segments = 100

    obj_info = object_types.get(type(line))
    if obj_info is None:
        return

    speed_attr = obj_info['speed_attr']
    point_attrs = obj_info['point_attrs']

    control_points = np.array([[copy.copy(getattr(line, point_attr).x), copy.copy(getattr(line, point_attr).y)]
                               for point_attr in point_attrs])

    curve = bezier_curve(control_points, num_segments)

    if isinstance(speed_attr, tuple):
        speed_attr_value = (getattr(line, speed_attr[0]), getattr(line, speed_attr[1]))
    else:
        speed_attr_value = getattr(line, speed_attr, None)
    if isinstance(speed_attr_value, tuple):
        speeds = np.linspace(speed_attr_value[0], speed_attr_value[1], num_segments - 1)
    else:
        speeds = np.linspace(speed_attr_value, speed_attr_value, num_segments - 1)

    spot_sizes = np.linspace(line.bp.spot_size, line.bp.spot_size, num_segments - 1)

    curve_array = np.stack([curve[:-1], curve[1:]], axis=1).reshape(-1, 2, 2)
    lc = mpl.collections.LineCollection(curve_array, cmap=cmap)
    lc.set_array(np.array(speeds))
    lc.set_linewidth(spot_sizes * 0.01)
    ax.add_collection(lc)
    if show_control_points:
        t = mpl.markers.MarkerStyle(marker='*')
        t._transform = t.get_transform().rotate_deg(180)
        control_points = np.array([[copy.copy(getattr(line, point_attr).x), copy.copy(getattr(line, point_attr).y)]
                                   for point_attr in point_attrs])
        control_params = [control_points, t]
    if show_control_points:
        return [curve_array[-1], spot_sizes[-1], control_params, speeds]
    else:
        return [curve_array[-1], spot_sizes[-1], speeds] 

def notebook_viewer(objects, show_control_points=False):
    """Create an interactive viewer for lines and curves."""
    objects = expand_objects(objects)
    object_number = widgets.IntText(value=len(objects), description='Max Objects:', min=1, max=len(objects))
    widgets.interact(plot_lines_and_points, objects=widgets.fixed(objects), upper_lim=(1, len(objects), 1), description = 'Index of objects',
                     object_number=object_number, show_control_points=widgets.fixed(show_control_points),
                     layout=widgets.Layout(width='50%'), continuous_update=False)
from functools import reduce
from itertools import chain
from sys import maxsize
import matplotlib
matplotlib.use('agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.patches import BoxStyle, Rectangle, FancyBboxPatch

from dooble.marble import Operator, Observable, Item


POINTS_PER_INCH = 72.0
DEFAULT_WIDTH = 6.4         # inches
DEFAULT_LAYER_HEIGHT = 0.7  # inches


def render_to_file(marble, filename, theme, dpi=100,
                   width=DEFAULT_WIDTH, layer_height=DEFAULT_LAYER_HEIGHT):
    layers = len(marble.layers)
    height = layers * layer_height
    points_per_layer = layer_height * POINTS_PER_INCH

    # Convert "logical" y units to points
    def plt_y(y):
        return (layers - y - 0.5) * points_per_layer

    # Setup up our figure
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    ax.set_axis_off()

    # Draw higher-order observable links
    for link in marble.higher_order_links:
        ax.plot(
            [link.from_x, link.to_x],
            [plt_y(link.from_y), plt_y(link.to_y)],
            scalex=True, scaley=False,
            color=theme.timeline_color, linestyle='-',
            linewidth=2)

    # Draw emission links
    for link in marble.emission_links:
        ax.plot(
            [link.from_x, link.to_x],
            [plt_y(link.from_y) - 0.21, plt_y(link.to_y) + 0.21],
            color=theme.emission_color, linestyle=':',
            linewidth=1, marker=7, markevery=[1])

    for layer_index, layer in enumerate(marble.layers):
        if type(layer) is Observable:
            observable = layer
            marker = 5
            if layer.completed is not None:
                marker = '|'
            elif layer.error is not None:
                marker = 'x'

            # Draw time line
            ax.plot(
                [observable.start, observable.end],
                [plt_y(layer_index), plt_y(layer_index)],
                color=theme.timeline_color, linestyle='-', linewidth=2, solid_capstyle='round',
                marker=marker, markersize=13, markevery=[1], markeredgewidth=2)

            # label
            if observable.label is not None:
                ax.text(observable.start, plt_y(layer_index), '@' + observable.label + '@',
                        family='monospace',
                        bbox=dict(
                            boxstyle=BoxStyle(stylename='square', pad=0.42),
                            edgecolor=theme.label_edge_color,
                            facecolor=theme.label_face_color,
                        ),
                        horizontalalignment='center', verticalalignment='center'
                )

            # items text
            for item in observable.items:
                text = str(item.item) if type(item) is Item else ' '
                ax.text(item.at, plt_y(layer_index), text,
                        family='monospace',
                        bbox=dict(
                            boxstyle=BoxStyle(stylename='round', pad=0.15, rounding_size=0.3),
                            edgecolor=theme.item_edge_color,
                            facecolor=theme.item_face_color,
                        ),
                        horizontalalignment='center', verticalalignment='center'
                )

        elif type(layer) is Operator:
            operator = layer
            x = (operator.end + operator.start) / 2
            y = plt_y(layer_index)
            ax.add_patch(Rectangle((0, y - 12), 2*x, 24,
                edgecolor=theme.operator_edge_color,
                facecolor=theme.operator_face_color,
            ))
            ax.text(
                (operator.end + operator.start) / 2, y,
                ' ' + operator.text + ' ',
                family='monospace',
                horizontalalignment='center', verticalalignment='center'
            )

    plt.savefig(filename, dpi=fig.dpi)
    plt.close()

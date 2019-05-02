import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, BoxStyle
import numpy as np
from dooble.marble import Operator, Observable, Item

area = np.pi*100
end_area = np.pi*50


def render_to_file(marble, filename, theme):
    height = len(marble.layers) * 0.7
    fig, ax = plt.subplots(figsize=(6.4, height), dpi=100)
    ax.set_axis_off()

    def plt_y(y):
        return len(marble.layers) - y - 1

    # higher observable links
    for link in marble.higher_order_links:
        ax.plot(
            [link.from_x, link.to_x],
            [plt_y(link.from_y), plt_y(link.to_y)],
            color=theme.timeline_color, linestyle='-',
            linewidth=2)

    # emission links
    for link in marble.emission_links:
        ax.plot(
            [link.from_x, link.to_x],
            [plt_y(link.from_y) - 0.21, plt_y(link.to_y) + 0.21],
            color=theme.emission_color, linestyle=':',
            linewidth=1, marker=7, markevery=[1])

    for layer_index, layer in enumerate(marble.layers):
        if type(layer) is Observable:
            observable = layer
            marker = 9
            if layer.completed is not None:
                marker = '|'
            elif layer.error is not None:
                marker = 'x'

            # time line
            ax.plot(
                [observable.start, observable.end],
                [plt_y(layer_index), plt_y(layer_index)],
                color=theme.timeline_color, linestyle='-', linewidth=2, solid_capstyle='round',
                marker=marker, markersize=13, markevery=[1], markeredgewidth=2)

            # label
            if observable.label is not None:
                ax.scatter(
                    [observable.start], [plt_y(layer_index)],
                    edgecolors=theme.operator_edge_color, 
                    color=theme.label_color, 
                    linewidth=2)
                ax.text(observable.start, plt_y(layer_index), observable.label,
                    horizontalalignment='center', verticalalignment='center'
                )

            # items text
            for item in observable.items:
                text = str(item.item) if type(item) is Item else ''
                ax.text(item.at, plt_y(layer_index), ' ' + text + ' ',
                        bbox=dict(
                            boxstyle=BoxStyle(stylename='round', pad=0.42, rounding_size=0.7),
                            facecolor=theme.item_color,
                            edgecolor=theme.operator_edge_color
                        ),
                        horizontalalignment='center', verticalalignment='center')

        elif type(layer) is Operator:
            operator = layer
            y = plt_y(layer_index) - 0.15
            ax.add_patch(Rectangle(
                (operator.start, y), operator.end - operator.start, 0.34,
                edgecolor=theme.operator_edge_color,
                facecolor=theme.operator_color,
                linewidth=2))
            ax.text(
                (operator.end + operator.start) / 2, y + 0.15,
                operator.text,
                horizontalalignment='center', verticalalignment='center')

    plt.savefig(filename, dpi=fig.dpi)
    plt.close()

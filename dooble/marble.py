from collections import namedtuple

Item = namedtuple('Item', ['item', 'at'])
ObsItem = namedtuple('ObsItem', ['at'])
Link = namedtuple('Link', [ 'from_x', 'from_y', 'to_x', 'to_y'])


class Observable(object):
    def __init__(self, start, end=None, is_child=False):
        self.start = start
        self.end = end
        self.is_child = is_child
        self.items = []
        self.completed = None
        self.error = None

    def on_next_at(self, item, at):
        self.items.append(Item(item, at))

    def on_observable_at(self, at):
        self.items.append(ObsItem(at))

    def on_completed_at(self, at):
        self.completed = at
        self.end = at

    def on_error_at(self, at):
        self.error = at
        self.end = at

    def on_continued_at(self, at):
        self.end = at


class Operator(object):
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class Marble(object):
    def __init__(self):
        self.layers = []
        self.higher_order_links = []
        return

    def add_observable(self, observable):
        self.layers.append(observable)

    def add_operator(self, operator):
        self.layers.append(operator)

    def _compute_higher_order_links(self):
        def nearest_links(parents, childs):
            links = []
            for parent in parents:
                nearest = None
                for child in childs:
                    if nearest is None or abs(parent[0] - child[0]) < abs(parent[0] - nearest[0]):
                        nearest = child

                if nearest is not None:
                    links.append(Link(
                        from_x=parent[0], from_y=parent[1],
                        to_x=nearest[0], to_y=nearest[1],
                    ))

            return links

        childs = []
        parents = []
        links = []
        for layer_index, layer in enumerate(self.layers):
            if type(layer) is Operator:
                links.extend(nearest_links(parents, childs))
                childs = []
                parents = []
            elif type(layer) is Observable:
                if layer.is_child is True:
                    childs.append((layer.start, layer_index))
                else:
                    for item in layer.items:
                        if type(item) is ObsItem:
                            parents.append((item.at, layer_index))

        links.extend(nearest_links(parents, childs))
        return links

    def build(self):
        self.higher_order_links = self._compute_higher_order_links()

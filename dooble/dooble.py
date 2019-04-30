from collections import namedtuple
from dooble.marble import Marble, Observable, Operator


Theme = namedtuple('Theme', [
    'timeline_color',
    'emission_color',
    'item_color',
    'label_color',
    'operator_color',
    'operator_edge_color',
])

default_theme = Theme(**{
    'timeline_color':      '#337AB7',
    'emission_color':      '#C0C0C0',
    'item_color':          '#E0E8FF',
    'label_color':         '#337AB7',
    'operator_color':      '#F0F0F0',
    'operator_edge_color': '#337AB7',
})


def create_observable(layer):
    part = 0
    step = len(layer[part])

    part += 1
    is_child = False
    label = None
    if layer[part] == '+':
        is_child = True
        part += 1
        step += 1
    elif type(layer[part]) is str:
        label = layer[part]
        step += 1
        part += 1

    start = step - 1 if is_child is True or label is not None else step
    observable = Observable(start, is_child=is_child)
    if label is not None:
        observable.set_label(label)

    for ts in layer[part]:
        if 'ts' in ts and ts['ts'] is not None:
            step += 1
        else:
            item = ts['item']
            if item == '+':
                observable.on_observable_at(step)
            else:
                observable.on_next_at(item, step)
            step += len(item)

    part += 1
    completion = layer[part]

    if completion == '|':
        observable.on_completed_at(step)
    elif completion == '*':
        observable.on_error_at(step)
    else:
        observable.on_continued_at(step)

    return observable


def create_operator(layer):
    step = 0
    start = step

    content = layer[1]
    text = content.strip()

    step += 1
    operator = Operator(start, step + len(content) , text)

    return operator


def create_marble_from_ast(ast):
    marble = Marble()

    for layer in ast:
        if 'obs' in layer and layer['obs'] is not None:
            marble.add_observable(create_observable(layer['obs']))
        elif 'op' in layer and layer['op'] is not None:
            marble.add_operator(create_operator(layer['op']))

    marble.build()
    return marble

from collections import defaultdict
from importlib import import_module


# Backends known to be widely supported
_COMMON_BACKENDS = 'agg', 'pdf', 'ps', 'svg'

# Map backend names to backend implementations
_AVAILABLE_BACKENDS = {}
for backend in _COMMON_BACKENDS:
    try:
        module_name = 'matplotlib.backends.backend_' + backend
        _AVAILABLE_BACKENDS[backend] = import_module(module_name)
    except ImportError:
        pass

# Map suffices / formats to a list of backends that support it (introspection)
_SUPPORTING_BACKENDS = defaultdict(list)
_counter = defaultdict(int)
for backend, implementation in _AVAILABLE_BACKENDS.items():
    FigureCanvas = getattr(implementation, 'FigureCanvas')
    for suffix in getattr(FigureCanvas, 'filetypes'):
        _SUPPORTING_BACKENDS[suffix].append(backend)
        _counter[backend] += 1

# Map each supported suffix to its preferred backend. In order of precedence:
# - The backend name and the suffix match exactly;
# - The backend is more specialized (has fewer supported types than the others);
# - The backend name and the suffix match partially;
# - The backend with the shortest name (longest substring match).
_PREFERRED_BACKENDS = {}
for suffix, supporting_backends in _SUPPORTING_BACKENDS.items():
    supporting_backends.sort(key=lambda backend: (suffix != backend,
                                                  _counter[backend],
                                                  suffix.find(backend) < 0,
                                                  len(backend)))
    _PREFERRED_BACKENDS['.' + suffix.lower()] = supporting_backends[0]

# Clean up
del _COMMON_BACKENDS, _AVAILABLE_BACKENDS, _SUPPORTING_BACKENDS, _counter


# Depending on available backends _PREFERRED_BACKENDS will now be something like
# {
#     '.eps':  'ps',
#     '.ps':   'ps',
#     '.pdf':  'pdf',
#     '.pgf':  'agg',
#     '.png':  'agg',
#     '.raw':  'agg',
#     '.rgba': 'agg',
#     '.svg':  'svg',
#     '.svgz': 'svg'
# }
#
# If the PIL/Pillow package is installed, we may find some more supported image
# formats, such as '.jpeg' and '.tiff', typically via the 'agg' backend.


def get_supported_suffices():
    """Return all supported suffices / image formats, lowercased and dotted."""
    return _PREFERRED_BACKENDS.keys()


def get_preferred_backend(suffix):
    """Return the preferred backend for given suffix, or None if unsupported."""
    return _PREFERRED_BACKENDS.get(suffix.lower())

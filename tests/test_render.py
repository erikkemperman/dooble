import unittest
import pathlib
from os import link, path
from tempfile import NamedTemporaryFile

from dooble.dooble import create_marble_from_ast, default_theme
from dooble.idl import Idl
from dooble.render import render_to_file

examples = path.abspath(path.join(path.dirname(__file__), '..', 'examples'))
marbles = {}
idl = Idl()

# Parse marbles from all *.txt files in the examples directory
for example in pathlib.Path(examples).glob('*.txt'):
    with example.open('r') as file:
        marbles[example.stem] = create_marble_from_ast(idl.parse(file.read()))


class TestRender(unittest.TestCase):

    def test_render(self):
        for suffix in '.eps', '.pdf', '.png', '.svg':
            for stem, marble in marbles.items():
                with NamedTemporaryFile(dir=examples, suffix=suffix) as test:
                    render_to_file(marble, test.name, default_theme)
                    ref = path.join(examples, stem + suffix)

                    # The ref file won't exist if you add a new suffix. You can
                    # create it by uncommenting the following snippet. Then you
                    # should verify the new file, and add it to git.
                    #
                    #   if not path.isfile(ref):
                    #       link(test.name, ref)
                    #
                    # If you need to recreate any of them, just throw them away
                    # before executing the snippet above, and commit the change.

                    test_size = path.getsize(test.name)
                    ref_size = path.getsize(ref)
                    ratio = test_size / ref_size

                    # Not really a proper image comparison, but if file sizes
                    # agree to within half a percent, it seems pretty likely
                    # that all is well.
                    self.assertAlmostEqual(ratio, 1.0, delta=0.005,
                                           msg=test.name + ' ~!~ ' + ref)

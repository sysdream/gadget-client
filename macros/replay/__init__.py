"""
Cheat at games just like old times with this Action Replay implementation
for Android!

Simply instanciate the Replay class and update the action replay as long as
you play. When the result count decreases to something satisfying, set the
values as you wish. Remember to refresh views in order for your modications
to be applied in most applications.

Example::

    from macros.replay import Replay

    # The initial score is 0.
    rep = Replay.new(app, 0)
    # Play some time, until the score reaches 20.
    rep.update(20)
    # Play some more time...
    rep.update(100)
    # Set the score!
    rep.set(999999)
"""

import os

from gadget.mapping import maptype, Object

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CLASS_NAME = "Replay"
MACRO_PATH = os.path.join(CURRENT_DIR, "Replay.apk")

@maptype('Replay')
class Replay(Object):
    """
    The actual implementation.
    """

    @classmethod
    def new(cls, app, needle, haystack=None, depth=3):
        if not haystack:
            haystack = app.listActivities()[0]
        macro = app.load(CLASS_NAME, MACRO_PATH)
        return macro(haystack, needle, depth)

    def update(self, value):
        """
        Update the filter value
        """
        self.applyFilter(value)
        self._refresh()

    def _refresh(self):
        """
        Store the flat list of results.
        """
        self._results = dict()
        for result in self.getResults():
            names = [str(field.getName()) for field in result]
            self._results[".".join(names)] = result

    def __repr__(self):
        """
        Pretty print.
        """
        return "<Replay with %d entities|%s>" % (
            len(self._results), ", ".join(self._results.keys()))

"""
Basic types defined as part of gadget library

User-defined mapped types are permitted thanks to the mapping system
as defined in the gadget.mapping module. Some of the most basic mapped
classes are defined as part of the gadget library itself for rapid
deployment and usage.
"""

from gadget.mapping import maptype, Object


@maptype('java.lang.Integer')
class Integer(Object):
    """
    Remote integer object
    """


@maptype('java.lang.String')
class String(Object):
    """
    Remote string object
    """

    def __repr__(self):
        """
        Pretty print
        """
        return "'%s'" % self._value

    def _refresh(self):
        """
        Grab the string value
        """
        self._value = self._service.get_value(self._entry_point, self._path)


@maptype('java.util.Map')
class Map(Object):
    """
    Remote map object

    Provides convenient Python-like dictionary access.
    """


@maptype('')
class Iterable(Object):
    """
    Remote iterable object

    Provides conenient Python-like list access and enumeration.
    """

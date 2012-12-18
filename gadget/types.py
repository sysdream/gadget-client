"""
Basic types defined as part of gadget library

User-defined mapped types are permitted thanks to the mapping system
as defined in the gadget.mapping module. Some of the most basic mapped
classes are defined as part of the gadget library itself for rapid
deployment and usage.
"""

from gadget.mapping import maptype, Object


@maptype('java.lang.Class')
class Class(Object):
    """
    Remote class object
    """

    def __call__(self, *args):
        """
        Create a new instance of this class

        Arguments passed to this method are automatically forwarded to the
        constructor.
        """
        # list of actual sent arguments
        objects = [arg if isinstance(arg, Object)
            else self._service.to_object(arg)
            for arg in args]
        arguments = [arg._getentrypoint() for arg in objects]
        return self._service.new_instance(
            self._entry_point,
            self._path,
            arguments)


@maptype('null')
class Null(Object):
    """
    Remote null
    """
    def __init__(self, service=None, types=None, entry_point=-1, path=[]):
        Object.__init__(self, service, types, -1 ,[])
    
    def __repr__(self):
        """
        Pretty print
        """
        return "<null>"

    def _getfields(self):
        return None

    def _getmethods(self):
        return None


@maptype('java.lang.Integer')
class Integer(Object):
    """
    Remote integer object
    """

    def __repr__(self):
        """
        Pretty print
        """
        return "%d" % self._value

    def _refresh(self):
        """
        Grab the Integer value
        """
        self._value = self._service.get_value(self._entry_point, self._path)

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

    def __len__(self):
        """
        Return the size of the map
        """
        return self.size()

    def __getitem__(self, key):
        """
        Get a remote item contained in the map
        """
        if self.containsKey(key):
            return self.get(key)
        else:
            raise IndexError()

    def __setitem__(self, key, value):
        """
        Put a remote value inside the remote map
        """
        self.put(key, value)


@maptype('')
class Iterable(Object):
    """
    Remote iterable object

    Provides convenient Python-like list access and enumeration.
    """


@maptype('android.app.Activity')
class Activity(Object):
    """
    Remote Android activity
    """

    def refresh(self):
        self.getWindow().getDecorView().postInvalidate()


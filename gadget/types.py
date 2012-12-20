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

    def __get__(self):
        """
        Value wrapping
        """
        return self._value

    def _refresh(self):
        """
        Grab the Integer value
        """
        self._value = int(self._service.get_value(self._entry_point, self._path))


@maptype('java.lang.Boolean')
class Boolean(Object):
    """
    Remote bool object
    """

    def __repr__(self):
        """
        Pretty print
        """
        return '%s' % self._value

    def _refresh(self):
        """
        Grab the boolean value
        """
        self._value = (self._service.get_value(self._entry_point, self._path)=='true')

    def __nonzero__(self):
        return self._value


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


@maptype('java.util.AbstractMap')
class Map(Object):
    """
    Remote map object

    Provides convenient Python-like dictionary access.
    """

    def __len__(self):
        """
        Return the size of the map
        """
        return int(self.size._value)

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


@maptype('java.util.Collection')
class Collection(Object):
    """
    Remote collection object

    Provides convenient Python-like list access and enumeration.
    """

    class Iterator:
        """
        Collection iterator

        Required to provide a for..in support
        """
        def __init__(self, obj):
            self._obj = obj
            self._iter = self._obj.iterator()

        def __iter__(self):
            return self
        
        def next(self):
            if self._iter.hasNext():
                return self._iter.next()
            else:
                raise StopIteration()

    def __repr__(self):
        return '<Collection object size=%d>' % self._M.size()._value

    def __in__(self, obj):
        return self.contains(obj)

    def __iter__(self):
        return self.Iterator(self)


@maptype('android.app.Activity')
class Activity(Object):
    """
    Remote Android activity
    """

    def refresh(self):
        """
        Activity refresh

        Calls the underlying window refresh routine
        """
        self.getWindow().getDecorView().postInvalidate()


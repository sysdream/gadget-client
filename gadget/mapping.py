"""
Type mapping management

Java types are mapped to Python types in a single common repository.
New type mappings may be declared using a simple class decorator on the
declared mapped class. The most specific mapping is always picked when
the mapping definitions are ambiguous.

Types ordering when performing mapping obeys the following rules:
* standard inheritance matches type parent relation
* interface implementation is more general than the type, yet less
  general than parent types
* an interface that is explicitely implemented at multiple levels is
  considered as specific as its most specific declaration

For instance, here an inheritance pattern:

                      ..........    ...............
            .-------->. IThing .    . IOtherThing .
            |         ..........    ...............
            |              ^               ^
            |              |               |
            |     .----------------.       |
            |     | Implementation |       |
            |     |                |       |
            |     '----------------'       |
            |              ^               |
            |              |               |
            |    .-------------------.     |
            |    | MoreSpecificClass | ----'
            |    '-------------------'
            |              ^
            |              |
            |   .---------------------.
            '---| OtherImplementation |
                '---------------------'

The resolution order is: OtherImplementation, IThing, MoreSpecificClass,
IOtherTHing, Implementation.

Let's assume the following type objects are defined on the Python side:
* ThingObject is mapped to IThing
* ImplementationObject is mapped to Implementation
* MoreSpecificObject is mapped to MoreSpecificClass and inherits from
  ImplementationObject

Applying the resolution rules results in:
* An instance of MoreSpecificClass is mapped to MoreSpecificObject
* An instance of Implementation is mapped to ImplementationObject
* An instance of OtherImplementation is mapped to ThingObject
"""

class Registry(object):
    """
    Class mapping registry

    Keeps a record of every mapped class and performs mapping
    resolution.
    """

    # the registry itself
    mappings = dict()

    @classmethod
    def register(cls, clazz, classname):
        """
        Register a new mapping

        Keyword arguments:
        classname -- the mapped Java class name
        """
        cls.mappings[classname] = clazz

    @classmethod
    def resolve(cls, classnames):
        """
        Resolve a mapping

        Keyword arguments:
        classnames -- list of Java class names

        Returns:
        the mapped Python class

        Exceptions:
        ValueError -- no available mapping (should never happen)
        """
        for classname in classnames:
            if classname in cls.mappings:
                return cls.mappings[classname]
        # should never raise since Object is registered for java.lang.object
        raise ValueError("No available mapping")


def maptype(*classnames):
    """
    Type mapping decorator

    Does not alter the class, so multiple decorators may be used
    instead of multiple mapping arguments:

       @maptype('java.lang.Integer', 'java.lang.Float')
       class Number(object):
           pass


       @maptype('java.lang.Integer')
       @maptype('java.lang.Float')
       class Number(object):
           pass

    Keword arguments:
    clazz    - the mapped Python type
    mappings - the corresponding Java types
    """
    def decorator(clazz):
        for classname in classnames:
            Registry.register(clazz, classname)
        # do not alter the class
        return clazz
    return decorator


@maptype('java.lang.Object')
class Object(object):
    """
    Base remote object that may be used as affectation, parameter, etc.

    Remote objects usually match one specific entry point in the remote
    entry point stack (see Fino documentation for details about entry
    points management).

    Evry type mapping class should inherit from this one.

    Some cache dictionaries are stored per instance:
    * the method cache is a dictionary, keys are method names, values
      are lists of modified method objects (multiple concrete methods)
    * class cache is a dictionary, keys are class names, values are
      modified class objects
    * field cache is a dictionary, keys are field names, values are
      modified objects
    (a modified object is a couple of modifiers and modified object, modifiers
    may be public, protected, private, static, etc. they are stored as strings)
    """

    def __init__(self, service, types, entry_point, path=[]):
        """
        Initialize the object

        Prepare the cache and save the object access properties

        Keyword arguments:
        service     -- the inspection service
        types       -- list of remote types of the current object
        entry_point -- the entry point number on the application side
        path        -- the path on the application side
        """
        self._service = service
        self._entry_point = entry_point
        self._types = types
        self._path = path
        self._field_cache = None
        self._method_cache = None
        self._refresh()

    def __repr__(self):
        """
        Pretty print
        """
        return "<%s object at %s.%s>" % (
            self._types[0], self._entry_point, str(self._path))

    def __cmp__(self, other):
        """
        Object comparison

        The default check verifies that both entry point and path are
        equal. The check is therefore not fully accurate and should not serve
        as criteria for decisions.
        """
        return (self._entry_point == other._entry_point
                and self._path == other._path)

    def __dir__(self):
        """
        Fields and methods listing

        List inner fields and methods with full signature as a dictionary.
        """
        return self._getfields().keys() + self._getmethods().keys()

    def __setattr__(self, name, value):
        """
        Set an attribute of the current object

        Attributes must be fields. Value must be an entrypoint.
        If not, the value is automatically converted to an entrypoint.
        """
        if name[0] == '_':
            object.__setattr__(self, name, value)
        else:
            # is the attribute a known field ?
            field = self._getfield(name)
            if field is not None:
                if isinstance(value, Object):
                    self._service.set_value(
                        field._entry_point,
                        field._path,
                        value._getentrypoint()
                    )
                else:
                    objval = self._service.to_object(value)
                    if objval is None:
                        objval = Registry.resolve(['null'])()
                    self._service.set_value(
                        field._entry_point,
                        field._path,
                        objval._getentrypoint()
                    )
                field._refresh()


    def __getattr__(self, name):
        """
        Access an attribute of the current object

        Attributes may be fields, methods or even inner classes.
        Resolution order is:
        * fields (no matter if public or private)
        * methods (no matter their visibility either)
        * classes

        Cache is refreshed using lazy mechanisms, ie. the method cache
        will not be refreshed if a field matches the attribute name.
        Methods returned as attributes are virtual methods: virtual method
        resolution will be performed on the Java side whenever the method
        object is called.
        """
        field = self._getfield(name)
        if field is not None:
            return field
        method = self._getmethod(name)
        if method is not None:
            return method
        raise AttributeError("Unknown attribute %s" % name)

    def _refresh(self):
        """
        Refresh the current field

        May be useful to primitive types wrappers for grabbing the field value
        for instance.
        """


    def _getfields(self):
        """
        Retrieve the list of fields of the remote object.
        """
        # if the field list needs to be refreshed
        if self._field_cache is None:
            self._field_cache = self._service.get_fields(
                self._entry_point, self._path)
        return self._field_cache


    def _getfield(self, name):
        """
        Access a field of the current object given its name

        There is no virtual field resolution mechanism in Java, so cache is
        simply refreshed and the matching field is returned if available.
        The cache is refreshed in two steps:
        * the list of fields is stored as keys (the value is None)
        * the field Object is generated when needed
        """
        # if the attribute is a field
        if name in self._getfields():
            modifiers, type_, field = self._field_cache[name]
            # if the specific field needs to be created
            if type(field) is int:
                field = self._service.get_field(
                    self._entry_point, self._path + [field])
                self._field_cache[name] = (modifiers, type_, field)
            # otherwise just refresh it
            field._refresh()
            return field

    def _getmethods(self):
        """
        Retrieve the remote object's methods
        """
        # if the method list needs to be refreshed
        if self._method_cache is None:
            self._method_cache = self._service.get_methods(
                self._entry_point, self._path)
        return self._method_cache


    def _getmethod(self, name):
        """
        Access a method of the current object given its name

        The method returned is a virtual method instance, ie. virtual method
        resolution will be performed at call time on the Java code side.
        """
        # if the attribute is a method
        if name in self._getmethods():
            # virtual method is simply a Method object with a string method
            # instead of integer method id
            return Method(self._service, self._entry_point, self._path, name)

    def _getentrypoint(self):
        """
        Get an entry point for the current object

        If the object is already an entry point, just return the entry point
        value. Otherwise, it is necessary to first push the object.
        """
        if len(self._path) > 0:
            self._entry_point = self._service.push(
                self._entry_point, self._path)
            self._path = []
        return self._entry_point


def instanceof(classname, instance = None):
    """
    Check if a remote object is an instance of the given class

    This function may be used without an instance for partial
    application.

    Keyword arguments:
    instance  -- the remote object
    classname -- the given class name
    """
    # if partial execution is requested
    if instance is None:
        def partial(instance):
            return classname in instance._types
        return partial
    else:
        return classname in instance._types


class Method(object):
    """
    Method representation

    Simply holds a method caracteristics and provides abstraction for
    method invocation.
    """

    def __init__(self, service, entry_point, path, method, signature = ""):
        """
        Initialize the method object

        If the method is a method name (as string), then the method object
        behaves like a virtual method and virtual method resolution is
        performed when invoked. If the method is a method identifier
        (as integer), then the method object behaves like a concrete method.

        Keyword arguments:
        service     -- the inspection service
        entry_point -- the entry point number on the application side
        path        -- the path on the application side
        method      -- represented method
        """
        self._service = service
        self._entry_point = entry_point
        self._path = path
        self._method = method
        self._signature = signature

    def __call__(self, *args):
        """
        Invoke the current method object with the given arguments

        Arguments may be Object instances or base types that will be
        cast as Object instances before actual method invocation.
        """
        # list of actual sent arguments
        objects = [arg if isinstance(arg, Object)
                   else self._service.to_object(arg)
                   for arg in args]
        arguments = [arg._getentrypoint() if arg is not None else None for arg in objects]
        # if the method is a virtual method
        if type(self._method is str):
            entry_point = self._service.virtual(
                self._entry_point, self._path, self._method, arguments)
        else:
            entry_point = self._service.invoke(
                self._entry_point, self._path, self._method, arguments)
        # return the result wrapped in an Object instance
        return entry_point

    def __repr__(self):
        """
        Pretty print
        """
        return "<%s method %s>" % (
            "virtual" if type(self._method) is str else "concrete",
            self._method if type(self._method) is str else self._signature)

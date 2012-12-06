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

    def register(cls, clazz, mapping):
        """
        Register a new mapping

        Keyword arguments:
        clazz   -- the mapped Python class
        mapping -- the mapped Java class name
        """
        cls.mappings[mapping] = clazz

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


def maptype(clazz, *mappings):
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
    for mapping in mappings:
        Registry.register(clazz, mapping)
    # do not alter the class
    return clazz


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

    # global entry point cache
    _entry_points = []

    def __init__(self, entry_point, path=[]):
        """
        Initialize the object

        Prepare the cache and save the object access properties

        Keyword arguments:
        entry_point -- the entry point number on the application side
        path        -- the path on the application side
        """
        self._entry_point = entry_point
        self._modifiers = modifiers
        self._path = path
        self._field_cache = None
        self._method_cache = None
        self._class_cache = None


class Class(object):
    """
    Class representation

    Simply holds a classname and provides abstraction for instanciation
    or class browsing. Class browsing is only available for static attributes
    and inner classes.
    """

    def __init__(self, classname):
        """
        Initialize the object
        """
        self._classname = classname
        # anonymous class object that is used to proxify requests to
        # static attributes and subclasses, no method proxification is allowed
        # because invocation would not have much sense
        self._object = None


class Method(object):
    """
    Method representation

    Simply holds a method caracteristics and provides abstraction for
    method invocation.
    """

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


@maptype('java.lang.Object')
class Object(object):
    """
    Base remote object that may be used as affectation, parameter, etc.

    Remote objects usually match one specific entry point in the remote
    entry point stack (see Fino documentation for details about entry
    points management).
    """

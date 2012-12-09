"""
Gadget protocol implementation

Gadget protocol basically relies on:
* IP for the routing layer
* TCP for the transport layer
* Homemade protocol for data transfer
* JSON for most of the encoding

Using a homemade protocol was a tough choice. Yet, no other protocol
like XML-RPC or usual SOAP implementations would allow full duplex
communication.

Gadget protocol messages are defined as follow.

 0             4                                             length
 +-------------+-------------------------- - - - -----------------+
 | length      |                  JSON payload                    |
 +-------------+-------------------------- - - - -----------------+
"""

class Protocol(object):
    """
    Baremetal protocol implementation

    Provides simple access to remote inspection service methods by simply
    proxifying them through the dedicated protocol.
    """

    def __init__(self, remote, app):
        """
        Connect to the remote end point

        Keyword arguments:
        remote -- address and port of the remote end point
        app    -- inspected application package
        """

    def _call(self, name, arguments):
        """
        Proxify a call to the remote end point and parse the result

        Keyword arguments:
        name      -- name of the remote method
        arguments -- list of arguments for the method
        """

    def __getattr__(self, name):
        """
        Proxify every call to the remote end point using the _call method
        """
        def proxy(arguments):
            """
            Proxy function
            """
            return self._call(name, arguments)
        # return the proxy
        return proxy


class Service(object):
    """
    Wrapping service over the protocol

    The service provides access to remote functions through more semantic
    wrappers with use of the type mapping module and classes.
    """

    def __init__(self, protocol):
        """
        Initialize the service
        """
        self.protocol = protocol

    def get_fields(self, entry_point, path):
        """
        List fields of a specific object

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object

        Returns:
        a dictionary with field names as keys and tuples of both modifiers
        and field identifier as value
        """

    def get_field(self, entry_point, path, field):
        """
        Get a specific field wrapped into an mapped class instance

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object
        field       -- the field identifier as returned by get_fields

        Returns:
        a mapped class instance for the object
        """

    def get_methods(self, entry_point, path):
        """
        List methods of a specific object

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object

        Returns:
        a dictionary with method names as keys and a list of tuples
        of both modifiers and concrete method object as value
        """

    def push(self, entry_point, path):
        """
        Push an object as an entry point

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object

        Returns:
        the new entry point for the object
        """

    def to_object(self, var):
        """
        Take a Python typed object and push it as a remote object

        Keyword arguments:
        var -- a Python typed object

        Returns:
        a mapped class instance for remote usage
        """

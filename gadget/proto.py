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

import socket
import json
import struct

from mapping import Registry, Method


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

        Exceptions:
        IOError -- connection to the remote end point failed
        """
        self._app = app
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(remote)
        self.connectApp()

    def __del__(self):
        """
        Disconnect the protocol instance
        """
        self._socket.close()

    @staticmethod
    def _call(socket, app, name, arguments):
        """
        Proxify a call to the remote end point and parse the result

        Keyword arguments:
        name      -- name of the remote method
        arguments -- list of arguments for the method
        """
        # send the request
        request = json.dumps([app, name] + list(arguments))
        message = struct.pack('>I', len(request)) + request
        socket.send(message)
        # wait for the answer
        length = socket.recv(4)
        assert len(length) == 4, IOError("Connection error while receiving")
        length = struct.unpack('>I', length)[0]
        # receive as many bytes from the tcp socket
        result = ''
        while len(result) < length:
            recv = socket.recv(length - len(result))
            if len(recv) == 0:
                break
            result += recv
        # always check the message length
        assert len(result) == length, IOError("Wrong message length")
        # decode the answer
        response = json.loads(result)
        if not response['success']:
            raise RuntimeError("Remote error, %s" % response['response'])
        return None if 'response' not in response else response['response']

    def __getattr__(self, name):
        """
        Proxify every call to the remote end point using the _call method
        """
        def proxy(*arguments):
            """
            Proxy function
            """
            return self._call(self._socket, self._app, name, arguments)
        # return the proxy
        return proxy


def list_applications(remote):
    """
    List applications that may be inspected on the given remote end point

    Keyword arguments:
    remote -- remote end point address and port

    Returns:
    the list of package names for Protocol instance initialization
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(remote)
    result = Protocol._call(sock, '', 'listApps', [])
    sock.close()
    return result


class Service(object):
    """
    Wrapping service over the protocol

    The service provides access to remote functions through more semantic
    wrappers with use of the type mapping module and classes.
    """

    def __init__(self, protocol):
        """
        Initialize the service

        Keyword arguments:
        protocol -- a protocol instance
        """
        self.protocol = protocol
        self.entry_points = None

    def get_entry_points(self):
        """
        List entry points as objects

        Returns:
        a list of entry point objects
        """
        # refresh the entry point cache if necessary
        if self.entry_points is None:
            self.refresh_entry_points()
        # refresh entry points
        for entry_point in self.entry_points:
            entry_point._refresh()
        return self.entry_points

    def refresh_entry_points(self):
        """
        Refresh the service entry point cache
        """
        self.entry_points = [
            self.get_field(index, [])
            for index in range(len(self.protocol.getEntryPoints()))]

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
        fields = self.protocol.getFields(entry_point, path)
        result = {}
        for index, field in enumerate(fields):
            name, signature = field.split(':')
            split = signature.split(' ')
            # remove the main type from the modifiers
            type_, modifiers = split[-1], split[:-1]
            # populate the result
            result[name] = (modifiers, type_, index)
        return result

    def get_field(self, entry_point, path):
        """
        Get a specific field wrapped into an mapped class instance

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object

        Returns:
        a mapped class instance for the object
        """
        if entry_point < 0:
            return None
        types = self.protocol.getTypes(entry_point, path)
        if len(types) == 0:
            return None
        return Registry.resolve(types)(self, types, entry_point, path)

    def get_class(self, classname):
        """
        Get a specific class object from class name

        Keyword arguments:
        classname -- the class name

        Returns:
        a mapped class instance for the class
        """
        clazz = self.protocol.getClass(classname)
        types = self.protocol.getTypes(clazz, [])
        if len(types) == 0:
            return None
        return Registry.resolve(types)(self, types, clazz, [])

    def get_value(self, entry_point, path):
        """
        Get the remote value of a specific field

        Mostly useful for primitive types.

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object
        """
        return self.protocol.getValue(entry_point, path)

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
        methods = self.protocol.getMethods(entry_point, path)
        result = {}
        for index, method in enumerate(methods):
            name, signature = method.split(':')
            split = signature.split(' ')
            # remote the return type and arguments from the modifiers
            modifiers, type_ = split[:-1], split[-1]
            # populate the result
            if not name in result:
                result[name] = []
            result[name].append(
                (modifiers, type_,
                 Method(self, entry_point, path, index, signature)))
        return result

    def new_instance(self, entry_point, path, args):
        """
        Perform a class instanciation

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object
        args        -- constructor args
        """
        return self.get_field(
            self.protocol.newInstance(
                entry_point, path, args),
            [])

    def virtual(self, entry_point, path, method, arguments):
        """
        Perform a virtual method call

        Virtual method call involves virtual method resolution on the Java side.
        The method name passed must be a string.

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object
        method      -- method name
        arguments   -- list of arguments entry points
        """
        return self.get_field(
            self.protocol.invokeMethodByName(
                entry_point, path, method, arguments),
            [])

    def push(self, entry_point, path):
        """
        Push an object as an entry point

        Keyword arguments:
        entry_point -- the object entry point
        path        -- path from the entry point to the object

        Returns:
        the new entry point for the object
        """
        return self.protocol.pushObject(entry_point, path)

    def to_object(self, var):
        """
        Take a Python typed object and push it as a remote object

        Keyword arguments:
        var -- a Python typed object

        Returns:
        a mapped class instance for remote usage
        """
        if type(var) is str:
            return self.get_field(self.protocol.pushString(var), [])
        elif type(var) is int:
            return self.get_field(self.protocol.pushInt(var), [])
        elif type(var) is bool:
            return self.get_field(self.protocol.pushBool(var), [])


class Application(object):
    """
    Top abstraction level class for remote application access

    Assume that the remote application name is already known and hides every
    implementation detail.
    """

    def __init__(self, remote, app):
        """
        Connect to the remote application and initialize the local object

        Keyword arguments:
        remote -- remote address and port
        app    -- remote application name
        """
        assert app in list_applications(remote), \
            RuntimeError("Cannot find the application")
        self.protocol = Protocol(remote, app)
        self.service = Service(self.protocol)

    def get_entry_points(self):
        """
        List the application entry points
        """
        return self.service.get_entry_points()

    entry_points = property(get_entry_points)

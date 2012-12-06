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

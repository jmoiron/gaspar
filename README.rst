gaspar
-------

Gaspar is a library for creating small, simple TCP daemons that parallelize CPU
intensive work with a simple and low-overhead request/response pattern.

It does this by forking off a number of worker processes, using eventlet to
handle incoming requests and the 0MQ push/pull message pattern to load
ballance work across the worker processes and receive responses.

running servers
---------------

Gaspar uses the terms ``producer`` and ``consumer`` for the process that receives
incoming requests and the processes that actually handle those requests.  To use
Gaspar, you need only to create a producer and a consumer, and then start the
producer::

    >>> import gaspar
    >>> def echo(message): return message
    >>> consumer = gaspar.Consumer(handler=echo)
    >>> producer = gaspar.Producer(consumer, 10123)
    >>> producer.start()

The ``start`` call will block, and at this point you will have a server which is
listening on port ``10123``, receiving requests, sending them to a number of workers
(default is the # of CPUs on your machine), and then replying based on the echo
handler.

requests
--------

Gaspar's default Producer takes requests on a simple naked TCP port.  These
requests are:

   * a 4-byte unsigned int in network-byte order (``struct.pack('!I', N)``)
   * a string of that length

The reply is simply a string followed by the termination of the socket.  The
convenience function ``gaspar.request("host:port", message)`` will send a
request and return the reply synchronously.

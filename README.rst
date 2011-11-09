gaspar
======

Gaspar is a library for creating small, simple TCP daemons that parallelize CPU
intensive work with a simple and low-overhead request/response pattern.

It does this by forking off a number of worker processes, using eventlet to
handle incoming requests and the 0MQ push/pull message pattern to load
ballance work across the worker processes and receive responses.


running servers
---------------

Gaspar uses the terms ``producer`` and ``consumer`` for the process that receives
incoming requests and the processes that actually handle those requests.  In the
0MQ documentation, these are called ``ventilator`` and ``sink``, and various
other terms are used throughout distributed systems literature.  To use Gaspar,
you need only to create a producer and a consumer, and then start the producer::

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
convenience function ``gaspar.client.request("host:port", message)`` will send a
request and return the reply synchronously.  It uses the basic ``socket``
libraries, so you can "green" it safely with eventlet or gevent's monkey
patching methods.

``gaspar.client`` also provides a function called ``pack`` which takes a string
and returns a new string with the 4-byte message length pre-pended.  If you
are using a gaspar daemon with async frameworks that are not greenlet based,
you can use this to cover that aspect of the client protocol.

limitations
-----------

formless request/response
~~~~~~~~~~~~~~~~~~~~~~~~~

Gaspar requests and responses are just strings.  There is no standard way to
serialize multiple arguments or return multiple values.  Because the nature of
the work being farmed out to such a daemon could be defeated by the wrong
calling semantics, these details are left to the ``Consumer`` implementation
and to postprocessing client responses.

single-server operation
~~~~~~~~~~~~~~~~~~~~~~~

Although the technologies in use (TCP and 0MQ) would allow for daemons to be
spread across systems, this wasn't an original design goal of Gaspar and it
is not currently supported.


why shouldn't I use celery?
---------------------------

The major "advantages" of Gaspar over Celery are its small size, conceptual
simplicity, and infrastructureless operation.  The purpose of Gaspar was to
make it very easy to remove CPU bound processes from a tight event based I/O
loop (like eventlet, gevent, tornado, et al), turn it into I/O wait, and
spread that work across multiple cores.

Celery serves a much broader range of purposes, is a lot more sophisticated,
and has features like delayed and recurrent execution that Gaspar lacks.  If
you have a number of tasks you need to execute asynchronously, Celery is
very good at this.


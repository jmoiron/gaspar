gaspar
-------

Gaspar is a microframework for creating small daemons that parallelize CPU
intensive work in a simple daemon that does request/response over TCP.

It does this by forking off a number of worker processes, using gevent to
handle incoming requests and the 0MQ request/reply message pattern to load
ballance work across the worker processes.


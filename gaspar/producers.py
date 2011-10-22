#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar producers."""

from gevent import sleep, socket
from gevent_zeromq import zmq
from gevent.pool import Pool
from gevent.server import StreamServer
from gevent.event import Event

class Producer(object):
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.blocking = False
        self.server = StreamServer((self.host, self.port), self.handler, spawn=Pool(1000))
        self.start_event = Event()
        self.stop_event = Event()

    def setup_zmq(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        port = socket.bind_to_random_port("tcp://%s" % self.host)
        self.zmq_port = port
        self.zmq_socket = socket
        self.zmq_context = context

    def start(self, blocking=True):
        self.blocking = blocking
        self.setup_zmq()
        if blocking:
            self.start_event.set()
            self.server.serve_forever()
            self.stop()
        else:
            self.server.start()
            self.start_event.set()

    def stop(self):
        self.server.stop()
        self.zmq_socket.close()
        self.stop_event.set()
        # let event listeners listening to this event run
        sleep(0)

    def handler(self, sock, address):
        print "New connection from %s:%s" % address
        sockfile = sock.makefile()
        request = sockfile.readline().strip()
        if not request:
            return
        self.zmq_socket.send(request)
        response = self.zmq_socket.recv()
        sockfile.write(response)


class SimpleProducer(Producer):
    def __init__(self, port, incoming, host='127.0.0.1'):
        self.incoming = incoming
        super(SimpleProducer, self).__init__()

    def handler(self, sock, address):
        self.incoming(sock, address)



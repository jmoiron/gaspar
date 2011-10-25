#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar producers."""

from socket import error

import eventlet
from eventlet.green import zmq
from eventlet.event import Event

zmqc = zmq.Context()

class Producer(object):
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.blocking = False
        self.server = eventlet.listen((self.host, self.port))
        self.start_event = Event()
        self.stop_event = Event()

    def setup_zmq(self):
        socket = zmqc.socket(zmq.REQ)
        port = socket.bind_to_random_port("tcp://%s" % self.host)
        self.zmq_port = port
        self.zmq_socket = socket

    def serve(self):
        self.start_event.send()
        while True:
            try:
                conn, addr = self.server.accept()
            except error:
                if self.stop_event.ready():
                    return
            eventlet.spawn(self.handler, conn, addr)

    def start(self, blocking=True):
        self.blocking = blocking
        self.setup_zmq()
        if blocking:
            self.serve()
        else:
            eventlet.spawn(self.serve)
            eventlet.sleep(0)

    def stop(self):
        self.zmq_socket.close()
        self.server.close()
        self.stop_event.send()
        # let event listeners listening to this event run
        eventlet.sleep(0)

    def handler(self, sock, address):
        print "New connection from %s:%s" % address
        sockfile = sock.makefile()
        request = sockfile.readline().strip()
        print "Request: %r" % request
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



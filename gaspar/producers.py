#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar producers."""

from socket import error

import eventlet
from eventlet.green import zmq
from eventlet.event import Event

class Producer(object):
    def __init__(self, port, host):
        self.port = port
        self.host = host
        self.blocking = False
        self.server = eventlet.listen((self.host, self.port))
        self.start_event = Event()
        self.stop_event = Event()

    def setup_zmq(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        port = socket.bind_to_random_port("tcp://%s" % self.host)
        self.zmq_port = port
        self.zmq_socket = socket
        self.zmq_context = context

    def serve(self):
        self.start_event.send()
        try:
            eventlet.serve(self.server, self.handler, 1000)
        except error:
            pass
        except:
            print "Exception caught from serve:"
            import traceback
            traceback.print_exc()

    def start(self, blocking=True):
        self.blocking = blocking
        self.setup_zmq()
        if blocking:
            self.serve()
        else:
            eventlet.spawn(self.serve)
            eventlet.sleep(0)

    def stop(self):
        #self.server.stop()
        self.zmq_socket.close()
        self.zmq_context.term()
        self.server.close()
        self.stop_event.send()
        # let event listeners listening to this event run
        eventlet.sleep(0)

    def handler(self, sock, address):
        print "New connection from %s:%s" % address
        sockfile = sock.makefile()
        request = sockfile.readline().strip()
        if not request:
            return
        #self.zmq_socket.send(request)
        #response = self.zmq_socket.recv()
        #sockfile.write(response)


class SimpleProducer(Producer):
    def __init__(self, port, incoming, host='127.0.0.1'):
        self.incoming = incoming
        super(SimpleProducer, self).__init__()

    def handler(self, sock, address):
        self.incoming(sock, address)



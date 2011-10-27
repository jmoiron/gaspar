#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple eventlet POC to check how to get ZMQ sockets working with
subprocesses spawned by a simple process."""

import os
import multiprocessing

import eventlet
from eventlet.green import zmq

#import zmq
#import time as eventlet

def log(msg):
    print "(%s) %s" % (os.getpid(), msg)

class Subprocess(multiprocessing.Process):
    def __init__(self, producer, sink, ip='127.0.0.1'):
        self.producer = producer
        self.sink = sink
        self.ip = ip
        super(Subprocess, self).__init__()

    def run(self):
        context = zmq._Context()
        producer = context.socket(zmq.PULL)
        sink = context.socket(zmq.PUSH)

        producer.connect('tcp://%s:%s' % (self.ip, self.producer))
        sink.connect('tcp://%s:%s' % (self.ip, self.sink))
        while True:
            task = producer.recv()
            if task == "shutdown":
                sink.send("Shutting down pid %s" % (os.getpid()))
                eventlet.sleep(0)
                return
            sink.send("Task: %s (%s)" % (task, os.getpid()))

class Server(object):
    def __init__(self, ip='127.0.0.1'):
        c = zmq._Context()
        self.ip = ip
        self.producer = c.socket(zmq.PUSH)
        self.sink = c.socket(zmq.PULL)
        self.producer_port = self.producer.bind_to_random_port('tcp://%s' % self.ip)
        self.sink_port = self.sink.bind_to_random_port('tcp://%s' % self.ip)

    def send(self, msg):
        self.producer.send(msg)

    def recv(self):
        return self.sink.recv()

server = Server()
subprocesses = [Subprocess(server.producer_port, server.sink_port) for i in range(2)]
for sub in subprocesses:
    sub.start()

# let everything connect
eventlet.sleep(0.1)

server.send("Hello, world")
server.send("Hello again, World")
server.send("Third time's a charm")
log(server.recv())
log(server.recv())
log(server.recv())
server.send("shutdown")
server.send("shutdown")
log(server.recv())
log(server.recv())


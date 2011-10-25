#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple gevent POC to check how to get ZMQ sockets working with
subprocesses spawned by a simple process."""

import os
import multiprocessing

import gevent
from gevent_zeromq import zmq

#import zmq
#import time as gevent

def log(msg):
    print "(%s) %s" % (os.getpid(), msg)

class Subprocess(multiprocessing.Process):
    def __init__(self, producer, sink, ip='127.0.0.1'):
        self.producer = producer
        self.sink = sink
        self.ip = ip
        super(Subprocess, self).__init__()

    def run(self):
        context = zmq.Context()
        log("New worker: %s" % id(context))
        producer = context.socket(zmq.PULL)
        sink = context.socket(zmq.PUSH)

        producer.connect('tcp://%s:%s' % (self.ip, self.producer))
        sink.connect('tcp://%s:%s' % (self.ip, self.sink))

        task = producer.recv()
        sink.send("Task: %s (%s)" % (task, os.getpid()))
        gevent.sleep(0)

class Server(object):
    def __init__(self, ip='127.0.0.1'):
        c = zmq.Context()
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
gevent.sleep(0.1)

log("Sending msg1")
server.send("Hello, world")
log("Sending msg2")
server.send("Hello again, World")
log(server.recv())
log(server.recv())


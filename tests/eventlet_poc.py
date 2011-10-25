#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple eventlet POC to check how to get ZMQ sockets working with
subprocesses spawned by a simple process."""

import os
import eventlet
import multiprocessing

from eventlet.green import zmq

def subprocess(ip, port):
    c = zmq.Context()
    print 'pid: %s, cid: %s' % (os.getpid(), id(c))
    socket = c.socket(zmq.REP)
    socket.connect("tcp://%s:%s" % (ip, port))
    print "connected to %s:%s" % (ip, port)
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    ret = poller.poll()
    print ret
    msg = socket.recv()
    print "Received msg: %s"
    socket.send("Reply\r\n")
    eventlet.sleep(0.05)

c = zmq.Context()
print 'pid: %s, cid: %s' % (os.getpid(), id(c))
socket = c.socket(zmq.REQ)
port = socket.bind_to_random_port('tcp://127.0.0.1')

# start subprocess
proc = multiprocessing.Process(target=subprocess, args=('127.0.0.1', port))
proc.start()

#print "sending msg"
socket.send("Hello, world\r\n")
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN|zmq.POLLOUT)
ret = poller.poll()
print ret
socket.recv()


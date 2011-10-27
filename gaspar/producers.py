#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar producers."""

import logging
import struct
from socket import error
from uuid import uuid4

import msgpack
import eventlet

from multiprocessing import Process, cpu_count
from eventlet.green import zmq
from eventlet.event import Event
from eventlet.pools import TokenPool

new_uuid = lambda: uuid4().hex
num_cpus = cpu_count()
logger = logging.getLogger(__name__)

class Producer(object):
    """The producer object, a server which takes requests from a TCP socket
    and forwards them to a zmq.PUSH socket that is PULLed from by workers
    that the producer starts.  The port is the TCP port to listen on, but
    the host is used by all sockets.  The consumer should be a Consumer
    object that will run in the worker processes and actually handle requests."""

    outstanding = {}

    def __init__(self, consumer, port, processes=num_cpus, host='127.0.0.1'):
        self.port = port
        self.host = host
        self.consumer = consumer
        self.consumer.initialize(self)
        self.init_events()
        self.pool = TokenPool(max_size=processes)
        self.pushpool = TokenPool(max_size=1)
        self.forker = Forker(self, consumer, processes)

    def init_events(self):
        # these events correspond to the server socket
        self.server_start = Event()
        self.server_stop = Event()
        # these events more or less correspond to the completion of the 
        # startup process, including forking
        self.running = Event()
        self.stopped = Event()

    def setup_zmq(self):
        """Set up a PUSH and a PULL socket.  The PUSH socket will push out
        requests to the workers.  The PULL socket will receive responses from
        the workers and reply through the server socket."""
        self.context = zmq.Context()
        self.push = self.context.socket(zmq.PUSH)
        self.pull = self.context.socket(zmq.PULL)
        self.push_port = self.push.bind_to_random_port("tcp://%s" % self.host)
        self.pull_port = self.pull.bind_to_random_port("tcp://%s" % self.host)
        # start a listener for the pull socket
        #eventlet.spawn(self.zmq_pull)

    def zmq_pull(self):
        while True:
            try:
                packed = self.pull.recv()
                print "Received response %s" % packed
                self.pool.put(None)
                eventlet.spawn(self.response_handler, packed)
            except zmq.ZMQError:
                eventlet.sleep(0.1)
                print "-"
            except:
                import traceback
                traceback.print_exc()
                return

    def serve(self):
        self.server_start.send()
        while True:
            try:
                conn, addr = self.server.accept()
            except error:
                if self.server_stop.ready():
                    return
            eventlet.spawn(self.request_handler, conn, addr)

    def start(self, blocking=True):
        self.server = eventlet.listen((self.host, self.port))
        self.server_addr = self.server.getsockname()
        self.setup_zmq()
        if blocking:
            self.serve()
        else:
            eventlet.spawn(self.serve)
            # ensure that self.serve runs now as calling code will
            # expect start() to have started the server even non-blk
            eventlet.sleep(0)

    def stop(self):
        self.push.close(linger=0.1)
        self.pull.close(linger=0.1)
        self.server.close()
        self.server_stop.send()
        # let event listeners listening to this event run
        eventlet.sleep(0)

    def request_handler(self, sock, address):
        logger.debug("connection from %s:%s" % address)
        try:
            size = struct.unpack('!I', sock.recv(4))[0]
            if size:
                request = sock.recv(size)
            else:
                sock.close()
                return
        except error:
            logger.warn("connection lost from %s:%s" % address)
            return
        token = self.pool.get()
        uuid = new_uuid()
        message = uuid + request
        self.outstanding[uuid] = (sock, address)
        self.pushpool.get()
        print "sending msg %s" % message
        print self.pushpool
        self.push.send(message)
        print "pushed message, releasing token"
        self.pushpool.put(None)
        print "push token released"

    def response_handler(self, content):
        print "Received response %s" % content
        uuid, response = content[:32], content[32:]
        sock, address = self.outstanding[uuid]

class Forker(object):
    """Encapsulate the forking and process management aspect of the Producer.
    This automatically starts when the producer starts, and automatically stops
    when the producer stops.  It shouldn't be necessary to customize the Forker."""
    def __init__(self, producer, consumer, processes):
        self.producer = producer
        self.num_processes = processes
        self.running = Event()
        self.stopped = Event()
        self.consumer = consumer
        eventlet.spawn(self.wait_for_start)
        eventlet.spawn(self.wait_for_stop)

    def wait_for_start(self):
        self.producer.server_start.wait()
        self.start()

    def wait_for_stop(self):
        self.producer.server_stop.wait()
        self.stop()

    def start(self):
        self.processes = [Process(target=self.subprocess) for i in range(self.num_processes)]
        for process in self.processes:
            process.start()
        if self.producer.stopped.ready():
            self.producer.stopped.reset()
        self.producer.running.send()

    def stop(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        self.producer.running.reset()
        self.producer.stopped.send()

    def subprocess(self):
        self.consumer.start()


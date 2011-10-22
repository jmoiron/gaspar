#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar consumers (workers)."""

from multiprocessing import cpu_count, Process
from gevent import spawn
from gevent_zeromq import zmq
from gevent.event import Event

num_cpus = cpu_count()

class Consumer(object):
    def __init__(self, producer, processes=num_cpus):
        self.producer = producer
        self.num_processes = processes
        self.running = Event()
        self.stopped = Event()
        spawn(self.wait_for_start)
        spawn(self.wait_for_stop)

    def wait_for_start(self):
        self.producer.start_event.wait()
        self.start()

    def wait_for_stop(self):
        self.producer.stop_event.wait()
        self.stop()

    def start(self):
        self.processes = [Process(target=self.subprocess) for i in range(self.num_processes)]
        for process in self.processes:
            process.start()
        self.running.set()

    def stop(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        self.running.clear()
        self.stopped.set()

    def subprocess(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.connect("tcp://%s:%s" % (self.producer.host, self.producer.zmq_port))
        while True:
            msg = socket.recv()
            reply = self.handle(msg)
            socket.send(reply)

    def handle(self, msg):
        print "Received message length %s" % (len(msg))
        return "Hello"


class SimpleConsumer(Consumer):
    def __init__(self, producer, handler, processes=num_cpus):
        self.handler = handler
        super(SimpleConsumer, self).__init__(producer, processes)

    def handle(self, msg):
        return self.handler(msg)

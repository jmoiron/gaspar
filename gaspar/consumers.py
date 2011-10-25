#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar consumers (workers)."""

from multiprocessing import cpu_count, Process
import eventlet
from eventlet.green import zmq
from eventlet.event import Event

num_cpus = cpu_count()

class Consumer(object):
    def __init__(self, producer, processes=num_cpus):
        self.producer = producer
        self.num_processes = processes
        self.running = Event()
        self.stopped = Event()
        eventlet.spawn(self.wait_for_start)
        eventlet.spawn(self.wait_for_stop)

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
        self.running.send()

    def stop(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        self.running.reset()
        self.stopped.send()

    def subprocess(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print "connection zmq tcp://%s:%s" % (self.producer.host, self.producer.zmq_port)
        socket.connect("tcp://%s:%s" % (self.producer.host, self.producer.zmq_port))
        print socket.fileno()
        print "connected, creating poller"
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN|zmq.POLLOUT)
        while True:
            print "polling"
            ret = poller.poll()
            print "polled: %s" % ret
            msg = socket.recv()
            print "Received msg: %s" % msg
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

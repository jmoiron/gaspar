#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gaspar tests."""

import gaspar
from unittest import TestCase

import os
import time
import eventlet

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def pong(message): return "pong" if message == "ping" else "pang"

def pause_2(message):
    time.sleep(2)
    return message

class ForkTest(TestCase):
    def setUp(self):
        self.producer = gaspar.Producer(gaspar.Consumer(pong), 0, processes=5)
        self.producer.start(blocking=False)
        self.producer.running.wait()

    def tearDown(self):
        if not self.producer.stopped.ready():
            self.producer.stop()

    def test_forking(self):
        forker = self.producer.forker
        self.assertEqual(len(forker.processes), 5)
        # use various checks to make sure the children are running
        for process in forker.processes:
            self.assertTrue(process.is_alive())
            self.assertTrue(process.pid)
            self.assertTrue(check_pid(process.pid))

        # make sure that stopping the producers stops the processes
        self.producer.stop()
        self.producer.stopped.wait()
        for process in forker.processes:
            self.assertFalse(process.is_alive())

"""
class CommunicationsTest(TestCase):
    def recv(self, message):
        self.received.append(message)
        return "Hello, %s" % message

    def connect(self, timeout=0.5, bufsize=1):
        client = eventlet.connect(('127.0.0.1', self.producer.server.getsockname()[1]))
        fobj = client.makefile(bufsize=bufsize)
        fobj._sock.settimeout(timeout)
        return fobj

    def setUp(self):
        from gaspar import Producer, SimpleConsumer
        self.received = []
        self.producer = Producer(0, '127.0.0.1')
        self.consumer = SimpleConsumer(self.producer, self.recv, processes=1)
        self.producer.start(blocking=False)
        self.consumer.running.wait()

    def tearDown(self):
        if not self.producer.stop_event.ready():
            self.producer.stop()

    def test_message_retrieval(self):
        client = self.connect()
        client.write("Mesage\r\n")
        client.flush()
        result = client.read()
        print "Received result: %s" % result
        client.close()
"""

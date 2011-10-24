#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gaspar tests."""

import gaspar
from unittest import TestCase

import os
import time
from gevent import sleep

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def noop(message): pass

def pause_2(message):
    time.sleep(2)
    return message

class ForkTest(TestCase):
    def setUp(self):
        self.producer = gaspar.Producer(0, '127.0.0.1')
        self.consumer = gaspar.SimpleConsumer(self.producer, noop, processes=5)
        self.producer.start(blocking=False)
        self.consumer.running.wait()

    def tearDown(self):
        if not self.producer.stop_event.is_set():
            self.producer.stop()

    def test_forking(self):
        self.assertEqual(len(self.consumer.processes), 5)
        # use various checks to make sure the children are running
        for process in self.consumer.processes:
            self.assertTrue(process.is_alive())
            self.assertTrue(process.pid)
            self.assertTrue(check_pid(process.pid))

        # make sure that stopping the producers stops the processes
        self.producer.stop()
        self.consumer.stopped.wait()
        for process in self.consumer.processes:
            self.assertFalse(process.is_alive())

'''
class CommunicationsTest(TestCase):
    def recv(self, message):
        self.received.append(message)
        return "Hello, %s" % message

    def connect(self, timeout=0.5, bufsize=1):
        from gevent import socket
        client = socket.create_connection(('127.0.0.1', self.producer.server.server_port))
        fobj = client.makefile(bufsize=bufsize)
        fobj._sock.settimeout(timeout)
        return fobj

    def setUp(self):
        from gaspar import Producer, SimpleConsumer
        self.received = []
        self.producer = Producer(0, '127.0.0.1')
        self.consumer = SimpleConsumer(self.producer, self.recv, processes=2)
        self.producer.start(blocking=False)
        self.consumer.running.wait()

    def tearDown(self):
        if not self.producer.stop_event.is_set():
            self.producer.stop()

    def test_message_retrieval(self):
        client = self.connect()
        client.write("Mesage\r\n")
        client.flush()
        result = client.read()
        print "Received result: %s" % result
        client.close()
'''


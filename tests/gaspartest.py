#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gaspar tests."""

import gaspar
from unittest import TestCase

import os
import time
import eventlet
from eventlet import greenpool
from eventlet import debug

#debug.hub_prevent_multiple_readers(False)

from gaspar.client import pack

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def pong(message):
    return "pong" if message == "ping" else "pang"

class ForkTest(TestCase):
    def setUp(self):
        self.producer = gaspar.Producer(gaspar.Consumer(pong), 0, processes=5)
        self.producer.start(blocking=False)
        self.producer.running.wait()

    def tearDown(self):
        if not self.producer.stopped.ready():
            self.producer.stop()
        self.producer.stopped.wait()
        eventlet.sleep(0.1)

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

class HelloTest(TestCase):

    def handle(self, message):
        return "Hello %s %s" % (message, os.getpid())

    def setUp(self):
        import gaspar
        consumer = gaspar.Consumer(self.handle)
        producer = gaspar.Producer(consumer, 0, processes=2)
        producer.start(blocking=False)
        producer.running.wait()
        self.producer = producer

    def tearDown(self):
        if not self.producer.stopped.ready():
            self.producer.stop()
        self.producer.stopped.wait()
        eventlet.sleep(0.1)

    def test_basic_echo(self):
        from uuid import uuid4
        num_messages = 10
        uuids = [uuid4().hex for x in range(num_messages)]
        pids = [process.pid for process in self.producer.forker.processes]

        def sendmsg(msg):
            client = eventlet.connect(self.producer.server_addr)
            client.send(pack(msg))
            return client.makefile().read()

        pool = greenpool.GreenPool(size=num_messages)
        responses = list(pool.starmap(sendmsg, [(u,) for u in uuids]))
        pool.waitall()

        self.assertEqual(len(responses), num_messages)
        for resp in responses:
            self.assertEqual(len(resp.split()), 3)
            hello, uuid, pid = resp.split()
            self.assertTrue(hello, "Hello")
            self.assertTrue(uuid in uuids)
            self.assertTrue(int(pid) in pids)


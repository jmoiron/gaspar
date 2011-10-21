#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""gaspar tests."""

from unittest import TestCase

import os
import time
from threading import Thread

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def pause_2(message):
    time.sleep(2)
    return message

class GasparTest(TestCase):
    def setUp(self):
        from gaspar import SimpleProducer, SimpleConsumer
        self.producer = SimpleProducer(port=43215)
        self.consumer = SimpleConsumer(self.producer, pause_2, processes=5)
        self.producer_thread = Thread(target=producer.start)
        self.producer_thread.start()

    def tearDown(self):
        self.producer.stop()
        self.producer_thread.join()

    def test_forking(self):
        self.assertEqual(len(self.consumer.processes), 5)
        # use various checks to make sure the children are running
        for process in self.consumer.processes:
            self.assertTrue(process.is_alive())
            self.assertTrue(process.pid)
            self.assertTrue(check_pid(process.pid))


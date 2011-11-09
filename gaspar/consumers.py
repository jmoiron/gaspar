#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar consumers (workers)."""

import os
import logging
import eventlet
from eventlet.green import zmq
from eventlet.event import Event

if not hasattr(zmq, '_Context'):
    zmq._Context = zmq.Context

logger = logging.getLogger(__name__)

class Consumer(object):
    """This object is instantiated with the parent producer when the
    worker processes are forked.  It PULL messages from the producer's push
    socket and PUSH responses to the producer's pull socket."""
    def __init__(self, handler=None):
        self.initialized = False
        self.handler = handler

    def initialize(self, producer):
        self.producer = producer
        self.initialized = True

    def start(self):
        """Start the consumer.  This starts a listen loop on a zmq.PULL socket,
        calling ``self.handle`` on each incoming request and pushing the response
        on a zmq.PUSH socket back to the producer."""
        if not self.initialized:
            raise Exception("Consumer not initialized (no Producer).")
        producer = self.producer
        context = zmq._Context()
        self.pull = context.socket(zmq.PULL)
        self.push = context.socket(zmq.PUSH)
        self.pull.connect('tcp://%s:%s' % (producer.host, producer.push_port))
        self.push.connect('tcp://%s:%s' % (producer.host, producer.pull_port))
        # TODO: notify the producer that this consumer's ready for work?
        self.listen()

    def listen(self):
        """Listen forever on the zmq.PULL socket."""
        while True:
            message = self.pull.recv()
            logger.debug("received message of length %d" % len(message))
            uuid, message = message[:32], message[32:]
            response = uuid + self.handle(message)
            self.push.send(response)

    def handle(self, message):
        """Handle a message.  If this producer was initialized with a handler,
        that handler is called with ``message`` as an argument, and its return
        value is sent over the zmq.PUSH socket back to the producer."""
        if self.handler:
            return self.handler(message)
        return message


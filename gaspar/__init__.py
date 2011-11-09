#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar is a library for creating small, simple TCP daemons that parallelize CPU
intensive work with a simple and low-overhead request/response pattern.

It does this by forking off a number of worker processes, using eventlet to
handle incoming requests and the 0MQ push/pull message pattern to load
ballance work across the worker processes and receive responses."""

from producers import Producer, Forker
from consumers import Consumer

VERSION = (1, 0)

__all__ = [p for p in dir() if not p.startswith('_')]


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gaspar request clients."""

import struct
import socket

def pack(message):
    size = struct.pack("!I", len(message))
    return size+message

def request(url, message):
    """Given a url (host:port) and a message, sends that message synchronously
    and returns the response."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host, port = url.split(':')
    port = int(port)
    s.connect((host, port))
    s.send(pack(message))
    data = s.makefile().read()
    s.close()
    return data


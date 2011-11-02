import time
from eventlet.green import zmq

print "Running size tests for REQ/REP sockets..."

addr = 'tcp://127.0.0.1:5555'
ctx = zmq.Context()
s1 = ctx.socket(zmq.REP)
s2 = ctx.socket(zmq.REQ)

s1.bind(addr)
s2.connect(addr)

time.sleep(0.3)

message = "-*" * 1024**2
print "sending %d bytes" % len(message)
s2.send(message)
received = s1.recv()
print "received %d bytes" % len(received)

s1.close()
s2.close()

print "Running size tests for PUSH/PULL sockets..."

s1 = ctx.socket(zmq.PULL)
s2 = ctx.socket(zmq.PUSH)

s1.bind(addr)
s2.connect(addr)

time.sleep(0.3)

print "sending %d bytes" % len(message)
s2.send(message)
received = s1.recv()
print "received %d bytes" % len(received)

s1.close()
s2.close()


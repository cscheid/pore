import threading
import socket
import struct
import numpy
import traceback
import os

##############################################################################

def clear(key):
    _ctx.clear(key)

def start(port_number=10943):
    _ctx.start(port_number)

def is_running():
    return _ctx._running

def stop():
    _ctx.stop()

def get(key):
    return _ctx.get(key)

def listen(key, call):
    _ctx.add_observer(key, call)

def unlisten(key, call):
    _ctx.remove_observer(key, call)

##############################################################################

class Lockable(object):

    def __init__(self):
        self._lock = threading.Lock()
        
    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._lock.release()
        return exception_type is None

def synchronized(method):
    def call_it(self, *args, **kwargs):
        with self:
            return method(self, *args, **kwargs)
    return call_it
        
class PoreServerContext(Lockable):

    def __init__(self):
        Lockable.__init__(self)
        self._verbose = True
        self._listener = None
        self._running = False
        self._data = {}
        self._observers = {}

    def set(self, key, value):
        with self:
            self._data[key] = value
        if key in self._observers:
            for caller in self._observers[key]:
                caller(value)

    def get(self, key):
        return self._data[key]

    @synchronized
    def clear(self, key):
        try:
            del self._data[key]
        except KeyError:
            print "pore doesn't know anything about", key

    @synchronized
    def add_observer(self, key, caller):
        self._observers.setdefault(key, []).append(caller)

    def remove_observer(self, key, caller):
        if key not in self._observers:
            raise Exception("key %s has no registered observers" % key)
        with self:
            self._observers[key].remove(caller)
    
    ##########################################################################

    @synchronized
    def start(self, port_number=10943):
        if self._listener:
            print "listener already running"
            return
        self._running = True
        self._listener = Listener(self, port_number)
        self._listener.start()
        print "Don't forget to stop the server before quitting!"

    @synchronized
    def stop(self):
        self._running = False
        self._listener.join()
        self._listener = None

        
##############################################################################
# pore listens on port 10943 ("1PORE" if you move your fingers one row
# up in qwerty keyboard)

# The protocol is as simple as it gets: client connects to the pore server,
# sends a single object, is done.

class Listener(threading.Thread):

    def __init__(self, server_ctx, port_number):
        threading.Thread.__init__(self)
        self._port_number = port_number
        self._ctx = server_ctx

    def run(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.settimeout(1.0)
        ss.bind(('localhost', self._port_number))
        ss.listen(5)
        
        while self._ctx._running:
            try:
                (clientsocket, address) = ss.accept()
                ct = DataCollector(clientsocket).start()
            except socket.timeout:
                pass
        print "poreserver done."

##############################################################################

class DataCollector(threading.Thread):

    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        
    def run(self):
        try:
            key = read_string(self.socket)
            (datatype, sz) = read_struct(self.socket, 'ii')
            result = numpy.zeros(sz / 4, dtype=datatype_map[datatype])
            remaining_bytes = sz
            while remaining_bytes > 0:
                buf = numpy.getbuffer(result, sz - remaining_bytes,
                                      remaining_bytes)
                received = self.socket.recv_into(buf, remaining_bytes)
                remaining_bytes -= received
            _ctx.set(key, result)
        except Exception, e:
            if ctx._verbose:
                print "DataCollector failed"
                traceback.print_exc(e)

##############################################################################

def read_struct(socket, spec):
    return struct.unpack(spec, safe_recv(socket, struct.calcsize(spec)))

def read_int(socket):
    return read_struct(socket, 'i')[0]

def read_string(socket):
    sz = read_int(socket)
    return safe_recv(socket, sz)

def safe_recv(s, size):
    result = []
    remaining_size = size
    while remaining_size > 0:
        d = s.recv(remaining_size)
        remaining_size -= len(d)
        result.append(d)
    return "".join(result)

##############################################################################

_ctx = PoreServerContext()

datatype_map = {0: numpy.dtype('int32'),
                1: numpy.dtype('float32')}

try:
    n = os.environ['PORE_PORT']
    port_number = int(n)
except KeyError, ValueError:
    port_number = 10943

start(port_number)

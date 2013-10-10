import socket
import numpy
import struct

def send(object, bucket_name='_pore_data', port_number=10943):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port_number))
    buf = numpy.getbuffer(object)
    s.sendall(struct.pack('i', len(bucket_name)))
    s.sendall(bucket_name)
    s.sendall(struct.pack('ii', datatype_invmap[object.dtype], len(object) * 4))
    s.sendall(buf)
    s.close()

##############################################################################

datatype_invmap = { numpy.dtype('int32'): 0,
                    numpy.dtype('float32'): 1 }

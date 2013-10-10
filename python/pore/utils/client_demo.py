import pore.client
import time
import scipy

while True:
    time.sleep(1)
    pore.client.send(scipy.array(scipy.randn(10), dtype='float32'))

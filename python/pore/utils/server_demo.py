# as dumb as it looks

import pore.server
import time

def ping(v):
    print "New vector!", v

pore.server.listen("_pore_data", ping)

while True:
    time.sleep(1)

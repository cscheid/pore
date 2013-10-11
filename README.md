# pore

Pore is a minimal array server (it lets you "pore over" your data).

It was originally created to debug a distributed face detector cascade
trainer, where I needed to look at float arrays coming from 30-50
concurrent processes in a cluster. It's probably not very useful
besides being a point in the design space of in-memory array storage
services.


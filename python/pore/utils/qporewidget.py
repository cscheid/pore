from PyQt4 import QtGui, QtCore

class Data(object): pass

class QPoreWidget(QtGui.QWidget):
    """QPoreWidget runs a pore server and keeps track of pore data.

    To track data under pore, use QPoreWidget.listen(name), and then
    connect to dataChanged. The signal is emitted with the name of the
    data that has been updated, and the data is stored at
    getattr(self.data, 'name').
    """

    def listen(self, name):
        def new_data(data):
            if not self.drop_emits:
                self.emit(QtCore.SIGNAL('new_data__pore'), (name, data))
        setattr(self.pore_data, name, None)
        # we delay the import so we only start the server when
        # absolutely necessary
        import pore.server
        pore.server.listen(name, new_data)
        
    def __update_data(self, (name, data)):
        setattr(self.pore_data, name, data)
        self.emit(QtCore.SIGNAL('dataChanged'), name)
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.pore_data = Data()
        self.drop_emits = False
        # for easy thread communication, we listen to signals emitted
        # by ourselves in a separate thread and use a queued
        # connection (Go Qt 4.5)
        self.connect(self, QtCore.SIGNAL('new_data__pore'),
                     self.__update_data, QtCore.Qt.QueuedConnection)

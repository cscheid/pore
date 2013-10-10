#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use('Qt4Agg')
import pylab
import time
from pore.utils.qporewidget import QPoreWidget

##############################################################################

class PoreBrowser(QPoreWidget):

    def __init__(self, parent=None):
        QPoreWidget.__init__(self, parent)
        self.connect(self, QtCore.SIGNAL('dataChanged'), self.redraw)

        self.setLayout(QtGui.QVBoxLayout())
        pylab.figure()
        mgr = pylab.get_current_fig_manager()
        self.layout().addWidget(mgr.window)
        panel = QtGui.QFrame()
        panel.setLayout(QtGui.QHBoxLayout())

        btn = QtGui.QPushButton("Force &Redraw")
        self.connect(btn, QtCore.SIGNAL('clicked()'), self.force_redraw)
        
        panel.layout().addWidget(btn)
        self._label = QtGui.QLabel("Discarded:")
        panel.layout().addWidget(self._label)
        self.layout().addWidget(panel)
        mgr.window.show()
        self._delta = 1.0
        self._last_redraw = time.time()
        self.listen('variances')
        self.listen('face_variances')

    def force_redraw(self):
        self.redraw(True)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            sys.exit(0)
        if event.key() == QtCore.Qt.Key_R:
            self.force_redraw()
            
    def redraw(self, name, force=False):
        d = time.time() - self._last_redraw
        force = force or (d > self._delta)
        if (force and
            self.pore_data.variances is not None and
            self.pore_data.face_variances is not None):
            self._last_redraw = time.time()
            v = self.pore_data.variances
            fv = self.pore_data.face_variances
            discarded = (v>2.5).sum() / float(len(v))
            self._label.setText("Discarded: %.03f" % discarded)
            r = v
            if len(r) > 0:
                pylab.clf()
                bins = pylab.hist(r, bins=50)[0]
                height = max(bins)
                for f in fv:
                    pylab.plot([f, f], [0, height], 'r-')
                pylab.draw()
##############################################################################

app = QtGui.QApplication(sys.argv)
browser = PoreBrowser()
browser.show()
sys.exit(app.exec_())

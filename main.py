import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, uic, QtWidgets
from PyQt5.QtGui import QImage, QPalette, QBrush, QPixmap, QIcon
from PyQt5.QtCore import QSize, pyqtSlot, QTimer
from PyQt5.uic import loadUi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import math
import sympy
from PIL import ImageTk, Image
from scipy import signal
import matplotlib.pyplot as plt
from sympy import *
from os import remove
from os import path
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
import os
havezero = 0

FPER = "spectra"
OUTDIR = "output"
try:
    os.stat( OUTDIR )
except:
    os.mkdir( OUTDIR )

int = 1

class MainWindow(QMainWindow):
    def __init__(self):
        # call QWidget constructor

        super( MainWindow, self ).__init__()
        loadUi( 'app.ui', self )
        #figure
        self.spectrum = plt.figure()
        self.canvas = FigureCanvas( self.spectrum )
        #self.toolbar = NavigationToolbar( self.canvas, self )
        #self.layout.addWidget( self.toolbar )
        self.layout.addWidget( self.canvas )
        pixmap = QPixmap('visible-spectrum.png')
        self.image1.setPixmap(pixmap)
        #camera
        # create a timer
        self.timer=QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        # set control_bt callback clicked  function
        self.control_bt.clicked.connect(self.controlTimer)
        self.savebutton.clicked.connect( self.save)
    # view camera
    def viewCam(self):
        global frame
        global ret
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.video_label.setPixmap(QPixmap.fromImage(qImg))
        #code
        ret, frame = self.cap.read()
        key = cv2.waitKey( 1 ) & 0xFF
        self.spectrum.clear()
        self.spectrum.add_subplot( 2, 1, 1 )
        if (int):
            global sy, yy, yyc,bgfreqr,bgfreqg,bgfreqb,bgfreqt,freqr,freqg,freqb,freqt
            sy = frame.shape[0]
            yy = np.array( range( sy ) )
            yyc = .8611 * yy + 310.0492
            bgfreqr = yy * 0
            bgfreqg = yy * 0
            bgfreqb = yy * 0
            bgfreqt = yy * 0

        freqr = frame[:, :, 2].sum( axis=1 );
        freqr = freqr - min( freqr )
        freqg = frame[:, :, 1].sum( axis=1 );
        freqg = freqg - min( freqg )
        freqb = frame[:, :, 0].sum( axis=1 );
        freqb = freqb - min( freqb )
        freqt = freqr + freqg + freqb

        plt.clf()

        # plt.axis([0, yy[-1], 100, 4E5])
        plt.axis( [yyc[0], yyc[-1], 100, 4E5] )
        plt.yscale( 'log' )

        plt.plot( yyc, freqt, color='gray' )
        plt.plot( yyc, freqr, color='red' )
        plt.plot( yyc, freqg, color='green' )
        plt.plot( yyc, freqb, color='blue' )

        # plt.axvline(180,color='blue');
        # plt.axvline(260,color='green');
        # plt.axvline(360,color='red');
        plt.axvline( 390, color='purple' );
        plt.axvline( 470, color='blue' );
        plt.axvline( 525, color='green' );
        plt.axvline( 590, color='yellow' );
        plt.axvline( 624, color='red' );
        plt.axvline( 625, color='orange' );
        plt.xlabel( "Wavelength (nm)" )
        plt.ylabel( "Illuminant Power" )
        #time.sleep(.2)
        self.canvas.draw()



    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.control_bt.setText("Stop")


        # if timer is started
        else:
            self.video_label.setStyleSheet( "background-color: rgb(0, 0, 0)" )
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.control_bt.setText("View")
            self.video_label.setStyleSheet( "background-color: rgb(0, 0, 0)" )

    def save(self):

        FPER = self.labelrute.text()
        fname = OUTDIR + "/" + FPER + "_" + str( time.time() )
        plt.savefig( fname + ".png", dpi=200 )
        cv2.imwrite( fname + "_raw.bmp", frame )
        dt = np.dtype(
            [('x', '|i'), ('l', 'd'), ('red', 'i'), ('green', 'i'), ('blue', 'i'), ('total', 'i'), ('bgred', 'i'),
             ('bggreen', 'i'), ('bgblue', 'i'), ('bgtotal', 'i')] )
        a = np.zeros( len( yy ), dt )
        a['x'] = yy;
        a['l'] = yyc;
        a['red'] = freqr;
        a['green'] = freqg;
        a['blue'] = freqb;
        a['total'] = freqt
        a['bgred'] = bgfreqr;
        a['bggreen'] = bgfreqg;
        a['bgblue'] = bgfreqb;
        a['bgtotal'] = bgfreqt
        np.savetxt( fname + '_data.txt', a, '%s', header="x l red green blue bgred bggreen bggblue", comments='' )
        #print("saved " + fname)
        time.sleep(.5)
        global name
        name = self.labelrute.text()
        noti = Notification( self )
        noti.show()


class Notification(QDialog):
    def __init__(self, parent=None):
        super( Notification, self ).__init__( parent )
        loadUi( 'notification.ui', self )
        self.buttonClose.clicked.connect( self.ok)
        self.labelName.setText(name)

    def ok(self):
        self.parent().show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec_())






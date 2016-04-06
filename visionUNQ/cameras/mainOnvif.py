# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 20:13:34 2016

@author: lilian
"""
# %% IMPORTS
from PyQt4 import QtGui, QtCore
import sys
import time
import cv2
import logging

from ui import principal
import CameraManager

# %% DECLARATIONS
class WorkThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        
    
    def __del__(self):
        self.wait()
    
    def load(self, ipcamera):
        self.camera = ipcamera
        self.start()
    
    
    def run(self):
        print int(QtCore.QThread.currentThreadId())
        url = self.camera.getStreamUri()
        logging.info("Abriendo captura desde " + url)
        self.camera.capture = cv2.VideoCapture(url)
        while (self.camera.capture.isOpened()):
            time.sleep(0.01)
            ret, frame = self.camera.capture.read()

            if ret == True:
                self.emit(QtCore.SIGNAL('update(PyQt_PyObject)'), frame)
                
            else:
                print('No se obtuvo frame, sale de while')
                break
            
        self.camera.capture.release()
        cv2.destroyAllWindows()

     

class PrincipalForm(QtGui.QMainWindow, principal.Ui_MainWindow):
    
    def __init__(self, parent=None):
        
        logging.info('Inicio de interfaz gráfica')
        super(PrincipalForm, self).__init__(parent)
        self.setupUi(self)
#        self.showMaximized()
        self.feLabelSelected = False
        self.ptzLabelSelected = False
        
        logging.debug('Inicializacion del manager de camaras')
        self.cameraManager = CameraManager.CameraManager()
        
        ''' Seleccion de frames de camaras '''
        self.feLabel.mousePressEvent = self.feLabel_selected
        self.ptzLabel.mousePressEvent = self.ptzLabel_selected
        self.mousePressEvent = self.labels_unselected
        
        ''' Accion de los botones '''
        self.btnCalibrate.clicked.connect(self.open_stream)
#        self.btn_Right.clicked.connect(self.ptzCam.moveRight)
#        self.btn_Right.clicked.connect(self.ptzCam.moveLeft)
#        self.btn_Down.clicked.connect(self.ptzCam.moveDown)
#        self.btn_Up.clicked.connect(self.ptzCam.moveUp)
        
#        self.btn_Down.clicked.connect(self.cameraManager.feCam.getTimestamp)
#        self.btn_Up.clicked.connect(self.cameraManager.feCam.setTimestamp)
        
        self.threadPool = []


        

    
    def open_stream(self):
        if self.cameraManager.ptzCam != None:
            self.threadPool.append(WorkThread())
            self.connect(self.threadPool[len(self.threadPool)-1], QtCore.SIGNAL("update(PyQt_PyObject)"), self.showPTZStreaming)
            self.threadPool[len(self.threadPool)-1].load(self.cameraManager.ptzCam)
        if self.cameraManager.feCam != None:
            self.threadPool.append(WorkThread())
            self.connect(self.threadPool[len(self.threadPool)-1], QtCore.SIGNAL("update(PyQt_PyObject)"), self.showFEStreaming)
            self.threadPool[len(self.threadPool)-1].load(self.cameraManager.feCam)
      
        
    def feLabel_selected(self, event):
        self.feLabelSelected = True
        self.feFrame.setLineWidth(3)
        
        self.ptzLabelSelected = False
        self.ptzFrame.setLineWidth(0)
        
        x = event.pos().x()
        y = event.pos().y()
        
    def ptzLabel_selected(self, event):
        self.ptzLabelSelected = True
        self.ptzFrame.setLineWidth(3)
        
        self.feLabelSelected = False
        self.feFrame.setLineWidth(0)
        
        x = event.pos().x()
        y = event.pos().y()
        
    def labels_unselected(self, event):
        self.ptzLabelSelected = False
        self.feLabelSelected = False
        self.feFrame.setLineWidth(0)
        self.ptzFrame.setLineWidth(0)

#    #override
#    def keyPressEvent(self, event):
#        print 'algo'
#        if event.key() == QtCore.Qt.Key_Right:
#            print 'Pa la derecha'
#            if self.ptzLabel_selected == True:
#                print 'Aca llamo a la camara pa que se mueva'

        
    #override    
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Esta seguro que desea salir?", 
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            if self.cameraManager.ptzCam != None:
                if self.cameraManager.ptzCam.capture.isOpened == True:
                    self.cameraManager.ptzCam.capture.release()
            
            if self.cameraManager.feCam != None:
                if self.cameraManager.feCam.capture.isOpened()==True:
                    self.cameraManager.feCam.capture.release()
            event.accept()
        else:
            event.ignore()


    def showPTZStreaming(self, frame):
#        ptzUrl = self.cameraManager.ptzCam.getStreamUri()
#        self.cameraManager.ptzCam.capture = cv2.VideoCapture(ptzUrl)
#        
#        while (self.cameraManager.ptzCam.capture.isOpened()):
#            ret, frame = self.cameraManager.ptzCam.capture.read()
#
#            if ret == True:

        image = QtGui.QImage(frame.tostring(), frame.shape[1], 
                         frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
     
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.ptzLabel.width(), self.ptzLabel.height(), 
                               QtCore.Qt.KeepAspectRatio)
        self.ptzLabel.setPixmap(pixmap)
        QtGui.QApplication.processEvents()
#            else:
#                break
#            
#        if self.cameraManager.ptzCam.capture.isOpened()==False:
#            print('No se pudo abrir la interfaz!')
#        
#        self.cameraManager.ptzCam.capture.release()
#        cv2.destroyAllWindows()
               
        
    def showFEStreaming(self, frame):
        image = QtGui.QImage(frame.tostring(), frame.shape[1], 
                                 frame.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
     
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.feLabel.width(), self.feLabel.height(), 
                               QtCore.Qt.KeepAspectRatio)
                               
        painter = QtGui.QPainter()
        painter.begin(pixmap)
        painter.setPen(QtGui.QColor(255, 0, 0))
        painter.setFont(QtGui.QFont('Decorative', 11))
        painter.drawText(self.feLabel.width()/2, self.feLabel.height()/2, '+')
        painter.end()

        self.feLabel.setPixmap(pixmap)
        QtGui.QApplication.processEvents()
        

# %% MAIN
def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Inicio')
    app = QtGui.QApplication(sys.argv)
    form = PrincipalForm()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()

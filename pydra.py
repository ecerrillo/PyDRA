#!/usr/bin/env python
# -*- coding: utf8 -*-
# $RCSfile: mdiimageviewer.pyw,v $ $Revision: 00c5d1c96a3b $ $Date: 2010/10/18 20:43:38 $

"""
based on PyQt MDI.py example and MDI Image Viewer Window.
"""

# ====================================================================

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QDate', 2)
sip.setapi('QTime', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QUrl', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

# ====================================================================

import os, sys, pylab, tempfile, imageviewer, icons_rc, methods
import pca,satur,ds,trfilter,grayband
from numpy import *
from scipy import misc,ndimage
from PIL import Image,ImageQt
from pyqtgraph.Qt import QtGui,QtCore
from formlayout import fedit

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

__version__ = "0.3.0"
COMPANY = "IAM"
DOMAIN = "iam.csic.es/pydra"
APPNAME = "PyDRA"

SETTING_RECENTFILELIST = "recentfilelist"
SETTING_FILEOPEN = "fileOpenDialog"
SETTING_SCROLLBARS = "scrollbars"
SETTING_STATUSBAR = "statusbar"
SETTING_SYNCHZOOM = "synchzoom"
SETTING_SYNCHPAN = "synchpan"

# ====================================================================
  

def toBool(value):
    """
    Module function to convert a value to bool.

    :param value: value to be converted
    :returns:     converted data
    """
    if value in ["true", "1", "True"]:
        return True
    elif value in ["false", "0", "False"]:
        return False
    else:
        return bool(value)

def strippedName(fullFilename):
    return QtCore.QFileInfo(fullFilename).fileName()

# ====================================================================
class auto_sl(QtGui.QDialog):
    
    text_auto = QtCore.pyqtSignal(str)
    
    def __init__(self, Dialog,parent=None):
        
        super(auto_sl, self).__init__(parent)
        
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(265, 122)
        Dialog.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        Dialog.setModal(False)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 80, 231, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalSlider = QtGui.QSlider(Dialog)
        self.horizontalSlider.setGeometry(QtCore.QRect(10, 40, 241, 22))
        self.horizontalSlider.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.horizontalSlider.setMaximum(15)
        self.horizontalSlider.setSliderPosition(3)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        text_auto = QtCore.pyqtSignal(str)
        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL('valueChanged(int)'), self.getValue)
        #self.horizontalSlider.valueChanged.connect(functools.partial(class_changed, self))
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Automatic recognition", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Adjust sensibility", None, QtGui.QApplication.UnicodeUTF8))

    def getValue(self,value):
        self.text_auto.emit(str(value))

class kmeanwidget(QtGui.QDialog):
     
    textSaved = QtCore.pyqtSignal(str)
    
    def apply(self):
        r1=zeros((self.idx.shape), dtype=int)
        g1=zeros((self.idx.shape), dtype=int)
        b1=zeros((self.idx.shape), dtype=int)
        z1=zeros((self.idx.shape), dtype=int)
        try:
                num=load('cclass.npy')
        except:
                num=methods.color_class()
                save('cclass',num)

        for i in range(0,self.iter):
                mask= self.idx==i
                print (i,self.matr_assign[i])
                k=self.matr_assign[i]
                r1[mask]=num[k,0]
                g1[mask]=num[k,1]
                b1[mask]=num[k,2]
                z1[mask]=self.matr_assign[i]
        
        r1[0,0]=0
        g1[0,0]=0
        b1[0,0]=0
        r1[1,1]=255
        g1[1,1]=255
        b1[1,1]=255
        mode = misc.toimage(array([r1,g1,b1]))
        compRGB=self.path+'/kmeans.tif'
        """file='/Users/Enrique/Downloads/kk3.tif'
        mode.save(file)"""
        mode.save(compRGB)
        matrixsv=self.path+'/kmatrix'
        savez(matrixsv,num,self.matr_assign,self.idx)
        self.emitTextSaved('apply')
        self.close()
        
    def change_backgrpic(self):
        if self.picture.currentText()=='Saturation': fullname=self.path+'/smatrix.npz'        
        if self.picture.currentText()=='Standard PCA' or self.picture.currentText()=='Third component' : fullname=self.path+'/pcamatrix.npz'
        if self.picture.currentText()=='Non-standard PCA': fullname=self.path+'/alt_pcamatrix.npz'
        if self.picture.currentText()=='Decorrelation': fullname=self.path+'/dsmatrix.npz'
        if self.picture.currentText()== self.fname or self.picture.currentText()=='Black background': fullname=self.path+'/cmatrix.npz'
        tmp=load(fullname)
        self.matrix = tmp['arr_0']
        if self.picture.currentText()== 'Black background':
            self.matrix = self.matrix-self.matrix
        if self.picture.currentText()=='Third component':
            self.matrix[0]=self.matrix[2]
            self.matrix[1]=self.matrix[2]
        self.load_image()
        
    def load_image(self):
        idxmasked=copy(self.matrix)
        mask = (self.idx==self.current_class)
        if self.check_visible.isChecked():
            idxmasked[1][mask]=255
            idxmasked[0][mask]=90
            idxmasked[2][mask]=90
        mode=misc.toimage(idxmasked)
        kmeanclass = self.path+'/tmp_class.tif'
        mode.save(kmeanclass)
        self.emitTextSaved('normal')
        
    def denoisech(self,value):
        self.denoise=value
        if self.denoise >0:
            self.idx=ndimage.median_filter(self.orig, self.denoise)
        self.load_image()
        
    def prev(self):
        if self.current_class > 0:
            self.current_class=self.current_class-1
            self.class_list.setCurrentRow(self.current_class)
            class_update='Class number: '+str(self.current_class+1)
            self.c_number.setText(class_update)
            self.load_image()
        elif self.current_class == 0:
            self.class_list.setCurrentRow(self.current_class)
            
    def next(self):
        if self.current_class < self.iter-1:
            self.current_class=self.current_class+1
            self.class_list.setCurrentRow(self.current_class)
            class_update='Class number: '+str(self.current_class+1)
            self.c_number.setText(class_update)
            self.load_image()
        elif self.current_class == self.iter:
            self.class_list.setCurrentRow(self.iter)
    
    def change_class(self):
        self.current_class = self.class_list.currentRow()
        col=int(self.matr_assign[self.current_class])
        self.assign_list.setCurrentRow(col)
        class_update='Class number: '+str(self.current_class+1)
        self.c_number.setText(class_update)
        ##añadir guardar clase siguiente
        self.load_image()
    
    def change_assign(self):
        self.matr_assign[self.current_class]=self.assign_list.currentRow() #asocia una clase con una categoría
        a = self.class_list.currentItem()
        a.setBackground(QtGui.QColor(self.num[self.assign_list.currentRow(),0],self.num[self.assign_list.currentRow(),1],self.num[self.assign_list.currentRow(),2]))
        self.assignation.setText(self.nclass[self.assign_list.currentRow()]) #cambia la etiqueta
        if self.check_auto.isChecked() and self.current_class < self.iter-1:
            self.current_class=self.current_class+1
            self.class_list.setCurrentRow(self.current_class)
            class_update='Class number: '+str(self.current_class+1)
            self.c_number.setText(class_update)
            self.load_image()
            
    def __init__(self, Form,path,idx,fname,parent=None):
        
        super(kmeanwidget, self).__init__(parent)
        
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(311, 468)
        Form.setModal(False)
        Form.setGeometry(0,5,311,468)
        self.check_visible = QtGui.QCheckBox(Form)
        self.check_visible.setGeometry(QtCore.QRect(10, 120, 121, 20))
        self.check_visible.setChecked(True)
        self.check_visible.setObjectName(_fromUtf8("check_visible"))
        self.check_auto = QtGui.QCheckBox(Form)
        self.check_auto.setGeometry(QtCore.QRect(160, 120, 121, 20))
        self.check_auto.setChecked(False)
        self.check_auto.setObjectName(_fromUtf8("check_auto"))
        self.picture = QtGui.QComboBox(Form)
        self.picture.setGeometry(QtCore.QRect(10, 90, 291, 26))
        self.picture.setObjectName(_fromUtf8("picture"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 70, 151, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.c_number = QtGui.QLabel(Form)
        self.c_number.setGeometry(QtCore.QRect(10, 10, 151, 16))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.c_number.setFont(font)
        self.c_number.setObjectName(_fromUtf8("c_number"))
        self.assignation = QtGui.QLabel(Form)
        self.assignation.setGeometry(QtCore.QRect(10, 35, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.assignation.setFont(font)
        self.assignation.setObjectName(_fromUtf8("assignation"))
        self.class_list = QtGui.QListWidget(Form)
        self.class_list.setGeometry(QtCore.QRect(10, 150, 141, 192))
        self.class_list.setObjectName(_fromUtf8("class_list"))
        self.assign_list = QtGui.QListWidget(Form)
        self.assign_list.setGeometry(QtCore.QRect(160, 150, 141, 192))
        self.assign_list.setObjectName(_fromUtf8("assign_list"))
        self.prev_butt = QtGui.QPushButton(Form)
        self.prev_butt.setGeometry(QtCore.QRect(6, 422, 81, 32))
        self.prev_butt.setObjectName(_fromUtf8("prev_butt"))
        self.apply_butt = QtGui.QPushButton(Form)
        self.apply_butt.setGeometry(QtCore.QRect(87, 422, 81, 32))
        self.apply_butt.setObjectName(_fromUtf8("apply_butt"))
        self.cancel_butt = QtGui.QPushButton(Form)
        self.cancel_butt.setGeometry(QtCore.QRect(158, 422, 81, 32))
        self.cancel_butt.setObjectName(_fromUtf8("cancel_butt"))
        self.next_butt = QtGui.QPushButton(Form)
        self.next_butt.setGeometry(QtCore.QRect(244, 422, 61, 32))
        self.next_butt.setObjectName(_fromUtf8("next_butt"))
        self.denoise_lb = QtGui.QLabel(Form)
        self.denoise_lb.setGeometry(QtCore.QRect(10, 360, 181, 16))
        self.denoise_lb.setObjectName(_fromUtf8("huetr_lb"))
        self.denoise = QtGui.QSlider(Form)
        self.denoise.setGeometry(QtCore.QRect(10, 390, 261, 22))
        self.denoise.setMaximum(25)
        self.denoise.setSingleStep(1)
        self.denoise.setPageStep(1)
        self.denoise.setOrientation(QtCore.Qt.Horizontal)
        self.denoise.setTickPosition(QtGui.QSlider.TicksBelow)
        self.denoise.setTickInterval(1)
        self.denoise.setValue(0)
        self.denoise.setObjectName(_fromUtf8("denoise"))
        
        #textSaved = QtCore.pyqtSignal(str)
        self.apply_butt.clicked.connect(self.apply)
        self.prev_butt.clicked.connect(self.prev)
        self.next_butt.clicked.connect(self.next)
        self.denoise.valueChanged.connect(self.denoisech)
        self.class_list.itemSelectionChanged.connect(self.change_class)
        self.assign_list.itemSelectionChanged.connect(self.change_assign)
        self.check_visible.stateChanged.connect(self.load_image)
        self.picture.activated.connect(self.change_backgrpic)
        QtCore.QObject.connect(self.cancel_butt, QtCore.SIGNAL(_fromUtf8("clicked()")), kmeanwidget.reject)
        
        self.current_class=0
        self.denoise=0
        self.orig=idx
        self.idx=idx
        self.path = path
        self.fname = fname
        
        flist = []
        flist.append(fname)
        if os.path.isfile(path+'/pcamatrix.npz') == True:
            flist.append('Standard PCA')
            flist.append('Third component')
        if os.path.isfile(path+'/alt_pcamatrix.npz') == True:
            flist.append('Non-standard PCA')
        if os.path.isfile(path+'/dsmatrix.npz') == True:
            flist.append('Decorrelation')
        if os.path.isfile(path+'/smatrix.npz') == True:
            flist.append('Saturation')
        flist.append('Black background')
        self.picture.clear()
        self.picture.addItems(flist)
        
        fullname=self.path+'/cmatrix.npz'
        tmp=load(fullname)
        self.matrix = tmp['arr_0']
        
        self.iter=amax(idx)+1
        self.matr_assign=zeros(self.iter,dtype=int) #Matriz donde se almacenan las clases asignadas
        
        self.num=load('cclass.npy')
        
        for i in range(0,self.iter):
            a= QtGui.QListWidgetItem('Class '+str(i+1))
            a.setBackground(QtGui.QColor(self.num[0,0],self.num[0,1],self.num[0,2]))
            self.class_list.addItem(a)
        self.class_list.setCurrentRow(0)
        
        self.nclass=load('nclass.npy')
        for i in range(0,len(self.nclass)):
            a=QtGui.QListWidgetItem(self.nclass[i])
            a.setBackground(QtGui.QColor(self.num[i,0],self.num[i,1],self.num[i,2]))
            self.assign_list.addItem(a)
        self.assign_list.setCurrentRow(0)
        
        
        self.retranslateUi(Form)
        
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Assignation of classes", None, QtGui.QApplication.UnicodeUTF8))
        self.check_visible.setText(QtGui.QApplication.translate("Form", "Set class visible", None, QtGui.QApplication.UnicodeUTF8))
        self.check_auto.setText(QtGui.QApplication.translate("Form", "Auto Mode", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Background image", None, QtGui.QApplication.UnicodeUTF8))
        self.c_number.setText(QtGui.QApplication.translate("Form", "Class number: 1", None, QtGui.QApplication.UnicodeUTF8))
        self.assignation.setText(QtGui.QApplication.translate("Form", "Rock", None, QtGui.QApplication.UnicodeUTF8))
        self.denoise_lb.setText(QtGui.QApplication.translate("Form", "Denoise (mean filter)", None, QtGui.QApplication.UnicodeUTF8))
        self.prev_butt.setText(QtGui.QApplication.translate("Form", "Previous", None, QtGui.QApplication.UnicodeUTF8))
        self.next_butt.setText(QtGui.QApplication.translate("Form", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.apply_butt.setText(QtGui.QApplication.translate("Form", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_butt.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

    def emitTextSaved(self,message):
        self.textSaved.emit(message)
        
class MdiChild(imageviewer.ImageViewer):
    """ImageViewer that implements <Space> key pressed panning."""

    def __init__(self, pixmap, filename, name):
        """:param pixmap: |QPixmap| to display
        :type pixmap: |QPixmap| or None
        :param filename: |QPixmap| filename
        :type filename: str or None
        :param name: name associated with this ImageViewer
        :type name: str or None"""
        super(MdiChild, self).__init__(pixmap, name)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._isUntitled = True
        self.currentFile = filename

    # ------------------------------------------------------------------

    @property
    def currentFile(self):
        """Current filename (*str*)."""
        return self._currentFile

    @currentFile.setter
    def currentFile(self, filename):
        self._currentFile = QtCore.QFileInfo(filename).canonicalFilePath()
        self._isUntitled = False
        self.setWindowTitle(self.userFriendlyCurrentFile)

    @property
    def userFriendlyCurrentFile(self):
        """Get current filename without path (*str*)."""
        if self.currentFile:
            return strippedName(self.currentFile)
        else:
            return ""

    # ------------------------------------------------------------------

    def keyPressEvent(self, keyEvent):
        """Overrides to enable panning while dragging.

        :param QKeyEvent keyEvent: instance of |QKeyEvent|"""

        assert isinstance(keyEvent, QtGui.QKeyEvent)
        if keyEvent.key() == QtCore.Qt.Key_Space:
            if (not keyEvent.isAutoRepeat() and
                not self.handDragging):
                self.enableHandDrag(True)
            keyEvent.accept()
        else:
            keyEvent.ignore()
        super(MdiChild, self).keyPressEvent(keyEvent)

    def keyReleaseEvent(self, keyEvent):
        """Overrides to disable panning while dragging.

        :param QKeyEvent keyEvent: instance of |QKeyEvent|"""
        assert isinstance(keyEvent, QtGui.QKeyEvent)
        if keyEvent.key() == QtCore.Qt.Key_Space:
            if (not keyEvent.isAutoRepeat() and
                self.handDragging):
                self.enableHandDrag(False)
            keyEvent.accept()
        else:
            keyEvent.ignore()
        super(MdiChild, self).keyReleaseEvent(keyEvent)

# ====================================================================

class MDIImageViewerWindow(QtGui.QMainWindow):
    """Views multiple images with optionally syncrhonized zooming & panning."""
    
    MaxRecentFiles = 5

    def __init__(self):
        super(MDIImageViewerWindow, self).__init__()

        self._recentFileActions = []
        self._handlingScrollChangedSignal = False

        self._mdiArea = QtGui.QMdiArea()
        self._mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self._mdiArea.subWindowActivated.connect(self.subWindowActivated)
        self.setCentralWidget(self._mdiArea)
        #self._mdiArea.setViewMode(QtGui.QMdiArea.TabbedView)

        self._mdiArea.subWindowActivated.connect(self.updateMenus)

        self._windowMapper = QtCore.QSignalMapper(self)
        self._windowMapper.mapped[QtGui.QWidget].connect(self.setActiveSubWindow)

        self._actionMapper = QtCore.QSignalMapper(self)
        self._actionMapper.mapped[str].connect(self.mappedImageViewerAction)
        self._recentFileMapper = QtCore.QSignalMapper(self)
        self._recentFileMapper.mapped[str].connect(self.openRecentFile)

        self.createActions()
        self.addAction(self._activateSubWindowSystemMenuAct)

        self.createMenus()
        self.updateMenus()
        self.createStatusBar()

        self.readSettings()
        self.updateStatusBar()


        self.setUnifiedTitleAndToolBarOnMac(True)

    # ------------------------------------------------------------------

    def createMappedAction(self, icon, text, parent, shortcut, methodName):
        """Create |QAction| that is mapped via methodName to call.

        :param icon: icon associated with |QAction|
        :type icon: |QIcon| or None
        :param str text: the |QAction| descriptive text
        :param QObject parent: the parent |QObject|
        :param QKeySequence shortcut: the shortcut |QKeySequence|
        :param str methodName: name of method to call when |QAction| is
                               triggered
        :rtype: |QAction|"""

        if icon is not None:
            action = QtGui.QAction(icon, text, parent,
                                   shortcut=shortcut,
                                   triggered=self._actionMapper.map)
        else:
            action = QtGui.QAction(text, parent,
                                   shortcut=shortcut,
                                   triggered=self._actionMapper.map)
        self._actionMapper.setMapping(action, methodName)
        return action

    def createActions(self):
        """Create actions used in menus."""
        #File menu actions
        self._openAct = QtGui.QAction(
            QtGui.QIcon(':/open.png'),
            "&Open...", self,
            shortcut=QtGui.QKeySequence.Open,
            statusTip="Open an existing file",
            triggered=self.open)
        
        self._openNEF = QtGui.QAction(
            "Open NEF", self,
            statusTip="Open an existing NEF file",
            triggered=self.openNEF)

        self._switchLayoutDirectionAct = QtGui.QAction(
            "Switch &layout direction", self,
            triggered=self.switchLayoutDirection)

        #create dummy recent file actions
        for i in range(MDIImageViewerWindow.MaxRecentFiles):
            self._recentFileActions.append(
                QtGui.QAction(self, visible=False,
                              triggered=self._recentFileMapper.map))

        self._exitAct = QtGui.QAction(
            QtGui.QIcon(':/exit.png'),
            "E&xit", self,
            shortcut=QtGui.QKeySequence.Quit,
            statusTip="Exit the application",
            triggered=QtGui.qApp.closeAllWindows)

        #Capture menu actions
        
        self._capture1 = QtGui.QAction(
            "Capture raw image from camera (Nikon)", self,
            triggered=self.capture1)
        
        #Processing actions
        self._pprc = QtGui.QAction(
            "Preprocessing", self,
            triggered=self.pprc)
            
        self._mask = QtGui.QAction(
            "Mask areas", self,
            triggered=self.mask)
                    
        self._apca = QtGui.QAction(
            "PCA", self,
            triggered=self.apca)
                    
        self._ads = QtGui.QAction(
            "Decorrelation Stretch", self,
            triggered=self.ads)

        self._akmeans = QtGui.QAction(
            "Tracing (K-Means classification)", self,
            triggered=self.akmeans)

        self._aihs = QtGui.QAction(
            "Saturation from 3rd component", self,
            triggered=self.aihs)
            
        self._aiter = QtGui.QAction(
            "Iterative analysis (saturation and PCA)", self,
            triggered=self.aiter)
    
        self._bm = QtGui.QAction(
            "Batch Analysis Mode", self,
            triggered=self.bm)
            
        self._cloudpca = QtGui.QAction(
            "Process PCA on XYZ file", self,
            triggered=self.cloudpca)
            
        self._setscale = QtGui.QAction(
            "Set image scale", self,
            triggered=self.setscale)
            
        self._greyband = QtGui.QAction(
            "Gray bands (components) enhacement", self,
            triggered=self.greyband)
       
        self._histograms = QtGui.QAction(
            "Generate histograms", self,
            triggered=self.histograms)
        
        self._rocker = QtGui.QAction(
            "Clean tracing", self,
            triggered=self.rocker)

        self._classtable = QtGui.QAction(
            "Manage classification table", self,
            triggered=self.classtable)
        
        self._autoclass = QtGui.QAction(
            "Automatic recognition of paintings", self,
            triggered=self.autoclass)
        
        #Trace            
        self._tracenoise = QtGui.QAction(
            "Remove small particles", self,
            triggered=self.tracenoise)
        
        #View menu actions
        self._showScrollbarsAct = QtGui.QAction(
            "&Scrollbars", self,
            checkable=True,
            statusTip="Toggle display of subwindow scrollbars",
            triggered=self.toggleScrollbars)

        self._showStatusbarAct = QtGui.QAction(
            "S&tatusbar", self,
            checkable=True,
            statusTip="Toggle display of statusbar",
            triggered=self.toggleStatusbar)

        self._synchZoomAct = QtGui.QAction(
            "Synch &Zoom", self,
            checkable=True,
            statusTip="Synch zooming of subwindows",
            triggered=self.toggleSynchZoom)

        self._synchPanAct = QtGui.QAction(
            "Synch &Pan", self,
            checkable=True,
            statusTip="Synch panning of subwindows",
            triggered=self.toggleSynchPan)

        #Scroll menu actions
        self._scrollActions = [
            self.createMappedAction(
                None,
                "&Top", self,
                QtGui.QKeySequence.MoveToStartOfDocument,
                "scrollToTop"),

            self.createMappedAction(
                None,
                "&Bottom", self,
                QtGui.QKeySequence.MoveToEndOfDocument,
                "scrollToBottom"),

            self.createMappedAction(
                None,
                "&Left Edge", self,
                QtGui.QKeySequence.MoveToStartOfLine,
                "scrollToBegin"),

            self.createMappedAction(
                None,
                "&Right Edge", self,
                QtGui.QKeySequence.MoveToEndOfLine,
                "scrollToEnd"),

            self.createMappedAction(
                None,
                "&Center", self,
                "5",
                "centerView"),
            ]

        #zoom menu actions
        separatorAct = QtGui.QAction(self)
        separatorAct.setSeparator(True)

        self._zoomActions = [
            self.createMappedAction(
                QtGui.QIcon(':/zoomin.png'),
                "Zoo&m In (25%)", self,
                QtGui.QKeySequence.ZoomIn,
                "zoomIn"),

            self.createMappedAction(
                QtGui.QIcon(':/zoomout.png'),
                "Zoom &Out (25%)", self,
                QtGui.QKeySequence.ZoomOut,
                "zoomOut"),

            #self.createMappedAction(
                #None,
                #"&Zoom To...", self,
                #"Z",
                #"zoomTo"),

            separatorAct,

            self.createMappedAction(
                None,
                "Actual &Size", self,
                "/",
                "actualSize"),

            self.createMappedAction(
                None,
                "Fit &Image", self,
                "*",
                "fitToWindow"),

            self.createMappedAction(
                None,
                "Fit &Width", self,
                "Alt+Right",
                "fitWidth"),

            self.createMappedAction(
                None,
                "Fit &Height", self,
                "Alt+Down",
                "fitHeight"),
           ]

        #Window menu actions
        self._activateSubWindowSystemMenuAct = QtGui.QAction(
            "Activate &System Menu", self,
            shortcut="Ctrl+ ",
            statusTip="Activate subwindow System Menu",
            triggered=self.activateSubwindowSystemMenu)

        self._closeAct = QtGui.QAction(
            "Cl&ose", self,
            shortcut=QtGui.QKeySequence.Close,
            shortcutContext=QtCore.Qt.WidgetShortcut,
            #shortcut="Ctrl+Alt+F4",
            statusTip="Close the active window",
            triggered=self._mdiArea.closeActiveSubWindow)

        self._closeAllAct = QtGui.QAction(
            "Close &All", self,
            statusTip="Close all the windows",
            triggered=self._mdiArea.closeAllSubWindows)

        self._tileAct = QtGui.QAction(
            "&Tile", self,
            statusTip="Tile the windows",
            triggered=self._mdiArea.tileSubWindows)

        self._cascadeAct = QtGui.QAction(
            "&Cascade", self,
            statusTip="Cascade the windows",
            triggered=self._mdiArea.cascadeSubWindows)

        self._nextAct = QtGui.QAction(
            "Ne&xt", self,
            shortcut=QtGui.QKeySequence.NextChild,
            statusTip="Move the focus to the next window",
            triggered=self._mdiArea.activateNextSubWindow)

        self._previousAct = QtGui.QAction(
            "Pre&vious", self,
            shortcut=QtGui.QKeySequence.PreviousChild,
            statusTip="Move the focus to the previous window",
            triggered=self._mdiArea.activatePreviousSubWindow)

        self._separatorAct = QtGui.QAction(self)
        self._separatorAct.setSeparator(True)

        self._aboutAct = QtGui.QAction(
            QtGui.QIcon(':/help.png'),
            "&About", self,
            statusTip="Show the application's About box",
            triggered=self.about)

        self._aboutQtAct = QtGui.QAction(
            QtGui.QIcon(':/qt.png'),
            "About &Qt", self,
            statusTip="Show the Qt library's About box",
            triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        """Create menus."""
        self._fileMenu = self.menuBar().addMenu("&File")
        self._fileMenu.addAction(self._openAct)
        self._fileMenu.addAction(self._openNEF)
        self._fileMenu.addAction(self._bm)
        self._fileMenu.addAction(self._switchLayoutDirectionAct)

        self._fileSeparatorAct = self._fileMenu.addSeparator()
        for action in self._recentFileActions:
            self._fileMenu.addAction(action)
        self.updateRecentFileActions()
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._exitAct)

        self._fileMenu = self.menuBar().addMenu("&Capture")
        self._fileMenu.addAction(self._capture1)

        self._fileMenu = self.menuBar().addMenu("&Preprocessing")
        self._fileMenu.addAction(self._pprc)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._mask)
        
        self._fileMenu = self.menuBar().addMenu("&Analysis")
        self._fileMenu.addAction(self._apca)
        self._fileMenu.addAction(self._ads)
        self._fileMenu.addAction(self._aihs)
        self._fileMenu.addAction(self._aiter)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._autoclass)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._classtable)

        self._fileMenu = self.menuBar().addMenu("&Tracing")
        self._fileMenu.addAction(self._akmeans)        
        self._fileMenu.addAction(self._tracenoise)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._rocker)
                
        self._fileMenu = self.menuBar().addMenu("&Tools")
        self._fileMenu.addAction(self._setscale)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._greyband)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._histograms)
        self._fileMenu.addSeparator()
        self._fileMenu.addAction(self._cloudpca)

        self._viewMenu = self.menuBar().addMenu("&View")
        self._viewMenu.addAction(self._showScrollbarsAct)
        self._viewMenu.addAction(self._showStatusbarAct)
        self._viewMenu.addSeparator()
        self._viewMenu.addAction(self._synchZoomAct)
        self._viewMenu.addAction(self._synchPanAct)

        self._scrollMenu = self.menuBar().addMenu("&Scroll")
        [self._scrollMenu.addAction(action) for action in self._scrollActions]

        self._zoomMenu = self.menuBar().addMenu("&Zoom")
        [self._zoomMenu.addAction(action) for action in self._zoomActions]

        self._windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self._windowMenu.aboutToShow.connect(self.updateWindowMenu)


        self.menuBar().addSeparator()

        self._helpMenu = self.menuBar().addMenu("&Help")
        self._helpMenu.addAction(self._aboutAct)
        self._helpMenu.addAction(self._aboutQtAct)
        
        self.deactiv(0)
        #self._tracenoise.setEnabled(False)
        
    def updateMenus(self):
        """Update menus."""
        hasMdiChild = (self.activeMdiChild is not None)

        self._scrollMenu.setEnabled(hasMdiChild)
        self._zoomMenu.setEnabled(hasMdiChild)

        self._closeAct.setEnabled(hasMdiChild)
        self._closeAllAct.setEnabled(hasMdiChild)

        self._tileAct.setEnabled(hasMdiChild)
        self._cascadeAct.setEnabled(hasMdiChild)
        self._nextAct.setEnabled(hasMdiChild)
        self._previousAct.setEnabled(hasMdiChild)
        self._separatorAct.setVisible(hasMdiChild)

    def updateRecentFileActions(self):
        """Update recent file menu items."""
        settings = QtCore.QSettings()
        files = settings.value(SETTING_RECENTFILELIST)
        numRecentFiles = min(len(files) if files else 0,
                             MDIImageViewerWindow.MaxRecentFiles)

        for i in range(numRecentFiles):
            text = "&%d %s" % (i + 1, strippedName(files[i]))
            self._recentFileActions[i].setText(text)
            self._recentFileActions[i].setData(files[i])
            self._recentFileActions[i].setVisible(True)
            self._recentFileMapper.setMapping(self._recentFileActions[i],
                                              files[i])

        for j in range(numRecentFiles, MDIImageViewerWindow.MaxRecentFiles):
            self._recentFileActions[j].setVisible(False)

        self._fileSeparatorAct.setVisible((numRecentFiles > 0))

    def updateWindowMenu(self):
        """Update the Window menu."""
        self._windowMenu.clear()
        self._windowMenu.addAction(self._closeAct)
        self._windowMenu.addAction(self._closeAllAct)
        self._windowMenu.addSeparator()
        self._windowMenu.addAction(self._tileAct)
        self._windowMenu.addAction(self._cascadeAct)
        self._windowMenu.addSeparator()
        self._windowMenu.addAction(self._nextAct)
        self._windowMenu.addAction(self._previousAct)
        self._windowMenu.addAction(self._separatorAct)

        windows = self._mdiArea.subWindowList()
        self._separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyCurrentFile)
            if i < 9:
                text = '&' + text

            action = self._windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild)
            action.triggered.connect(self._windowMapper.map)
            self._windowMapper.setMapping(action, window)

    def createStatusBarLabel(self, stretch=0):
        """Create status bar label.

        :param int stretch: stretch factor
        :rtype: |QLabel|"""
        label = QtGui.QLabel()
        label.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        label.setLineWidth(2)
        self.statusBar().addWidget(label, stretch)
        return label

    def createStatusBar(self):
        """Create status bar."""
        statusBar = self.statusBar()

        self._sbLabelName = self.createStatusBarLabel(1)
        self._sbLabelSize = self.createStatusBarLabel()
        self._sbLabelDimensions = self.createStatusBarLabel()
        self._sbLabelDate = self.createStatusBarLabel()
        self._sbLabelZoom = self.createStatusBarLabel()

        statusBar.showMessage("Ready")

    # ------------------------------------------------------------------

    @property
    def activeMdiChild(self):
        """Get active MDI child (:class:`MdiChild` or *None*)."""
        activeSubWindow = self._mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    # ------------------------------------------------------------------

    #overriden methods

    def closeEvent(self, event):
        if os.path.isfile(path+'/cmatrix.npz') == True:
            reply = QtGui.QMessageBox.question(self, 'Mensaje', "Save changes?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                print (self.sscale)
                if self.sscale==1:
                    savsac = QtGui.QMessageBox.question(self, 'Mensaje', "Overlay scale?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if savsac == QtGui.QMessageBox.No:
                        self.sscale=0
                folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Output Directory"))
                fileList = os.listdir(path)
                for fileName in fileList:
                    if fileName.endswith('.tif')==True:
                        name=path+'/'+fileName
                        origname = fileName.replace(".tif", "")
                        savef=folder+'/'+origname+'_'+os.path.basename(self.fname)+'.tif'
                        os.system('cp '+name+' '+savef)
                        if self.sscale==1:
                            os.system('convert -gravity SouthEast '+savef+' scalers.png -composite '+savef)
                        
            fileList = os.listdir(path)
            for fileName in fileList:
                os.remove(path+'/'+fileName)
            self._mdiArea.closeAllSubWindows()
            """Overrides close event to save application settings.
            :param QEvent event: instance of |QEvent|"""
            self._mdiArea.closeAllSubWindows()
            if self.activeMdiChild:
                event.ignore()
            else:
                self.writeSettings()
                event.accept()

    # ------------------------------------------------------------------
   
    
    @QtCore.pyqtSlot(str)
    def mappedImageViewerAction(self, methodName):
        """Perform action mapped to :class:`imageviewer.ImageViewer`
        methodName.

        :param str methodName: method to call"""
        activeViewer = self.activeMdiChild
        if hasattr(activeViewer, str(methodName)):
            getattr(activeViewer, str(methodName))()
    @QtCore.pyqtSlot()
    def toggleSynchPan(self):
        """Toggle synchronized subwindow panning."""
        if self._synchPanAct.isChecked():
            self.synchPan(self.activeMdiChild)

    @QtCore.pyqtSlot()
    def panChanged(self):
        """Synchronize subwindow pans."""
        mdiChild = self.sender()
        while mdiChild is not None and type(mdiChild) != MdiChild:
            mdiChild = mdiChild.parent()
        if mdiChild and self._synchPanAct.isChecked():
            self.synchPan(mdiChild)

    @QtCore.pyqtSlot()
    def toggleSynchZoom(self):
        """Toggle synchronized subwindow zooming."""
        if self._synchZoomAct.isChecked():
            self.synchZoom(self.activeMdiChild)

    @QtCore.pyqtSlot()
    def zoomChanged(self):
        """Synchronize subwindow zooms."""
        mdiChild = self.sender()
        if self._synchZoomAct.isChecked():
            self.synchZoom(mdiChild)
        self.updateStatusBar()

    @QtCore.pyqtSlot()
    def activateSubwindowSystemMenu(self):
        """Activate current subwindow's System Menu."""
        activeSubWindow = self._mdiArea.activeSubWindow()
        if activeSubWindow:
            activeSubWindow.showSystemMenu()

    @QtCore.pyqtSlot(str)
    def openRecentFile(self, filename):
        """Open a recent file.

        :param str filename: filename to view"""
        self.loadFile(filename)
        #split(filename)

    @QtCore.pyqtSlot()
    
    
    def open(self):
        """Handle the open action."""
        if os.path.isfile(path+'/cmatrix.npz') == True:
            reply = QtGui.QMessageBox.question(self, 'Mensaje', "Save changes?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                if self.sscale==1:
                    savsac = QtGui.QMessageBox.question(self, 'Mensaje', "Overlay scale?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if savsac == QtGui.QMessageBox.No:
                        self.sscale=0
                arica= QtGui.QMessageBox.question(self, 'Mensaje', "Incluir referencia sitio (Arica)?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if arica == QtGui.QMessageBox.Yes:
                    csv_arica.sitios(path)
                folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Output Directory"))
                fileList = os.listdir(path)
                for fileName in fileList:
                    if fileName.endswith('.tif')==True:
                        if fileName=='mini.tif':
                            pass
                        else:
                            name=path+'/'+fileName
                            origname = fileName.replace(".tif", "")
                            savef=folder+'/'+origname+'_'+os.path.basename(self.fname)+'.tif'
                            os.system('cp '+name+' '+savef)
                            if self.sscale==1:
                                os.system('convert -gravity SouthEast '+savef+' scalers.png -composite '+savef)
                    if fileName=='kmatrix.npz':
                        name=path+'/'+fileName
                        savef=folder+'/classifed_data.dra'
                        os.system('cp '+name+' '+savef)
                    if fileName=='kmatrix_edited.npz':
                        name=path+'/'+fileName
                        savef=folder+'/classifed_and_edited_data.dra'
                        os.system('cp '+name+' '+savef)
                    if fileName=='pcadata.txt':
                        name=path+'/'+fileName
                        savef=folder+'/pcadata.txt'
                        os.system('cp '+name+' '+savef)
                    if fileName=='sitio.txt':
                        name=path+'/'+fileName
                        savef=folder+'/sitio.txt'
                        os.system('cp '+name+' '+savef)
                    if fileName=='img_aerea.jpg':
                        name=path+'/'+fileName
                        savef=folder+'/img_aerea.jpg'
                        os.system('cp '+name+' '+savef)
                        
            fileList = os.listdir(path)
            for fileName in fileList:
                os.remove(path+'/'+fileName)
            self._mdiArea.closeAllSubWindows()
        fileDialog = QtGui.QFileDialog(self)
        settings = QtCore.QSettings()
        fileDialog.setNameFilters(["Image Files (*.jpg *.png *.tif)"])
        if not settings.contains(SETTING_FILEOPEN + "/state"):
            fileDialog.setDirectory(".")
        else:
            self.restoreDialogState(fileDialog, SETTING_FILEOPEN)
        fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if not fileDialog.exec_():
            return
        self.saveDialogState(fileDialog, SETTING_FILEOPEN)

        self.fname = fileDialog.selectedFiles()[0]
        self.loadFile(self.fname)
        matrix=methods.conversion(path,self.fname)
        matrixsv=path+'/cmatrix'
        savez(matrixsv,matrix)
        _,m,n=matrix.shape
        pre = Image.open(self.fname)
        if m > n:
            x=400
            y=int((n*400)/m)
        elif m==n:
            x=400
            y=400
        elif m<n:
            y=400
            x=int((m*400)/n)
        pre = pre.resize((y,x),Image.ANTIALIAS)
        mini=path+'/mini.tif'
        pre.save(mini)
        minmatrix=methods.conversion(path,mini)
        minmatrixsv=path+'/minimatrix'
        savez(minmatrixsv,minmatrix)
        self.rad = 8
        self.svf='nnnnn'
        self.sscale=0
        self.deactiv(1)
        
    def deactiv(self,a):
        self._mask.setEnabled(a)
        self._pprc.setEnabled(a)
        self._apca.setEnabled(a)
        self._aihs.setEnabled(a)
        self._aiter.setEnabled(a)
        self._ads.setEnabled(a)
        self._akmeans.setEnabled(a)
        self._autoclass.setEnabled(a)
        
    def classtable(self):
        try:
            num=load('cclass.npy')
            colorss=[]
            for i in range(0,7):
                colorss.append('#%02x%02x%02x' % tuple(num[i]))
            datalist=[('Rock',colorss[0]),('Paintings',colorss[1]),('Possible Paintings',colorss[2]),('Rock + Paintings',colorss[3]),('Erosion',colorss[4]),('Crack',colorss[5]),('Unclassificable',colorss[6])]
            num1=methods.color_class(num,datalist,0)
          
        except:
            pass
        save('cclass',num1)
        
    def autoclass(self):
        
        if os.path.isfile(path+'/pcamatrix.npz') == True: #comprueba que no exista la matriz de PCA en el disco duro
            filecheck='annnn'
        else:
            filecheck='nnnnn'
        
        if os.path.isfile(path+'/smatrix.npz') == False:
            methods.satur(path,1,False,filecheck,1,self.rad)
        self.idx,_=methods.k_means(40,'smatrix',path,'nnnnn')
        

        tmp=load(path+'/pcamatrix.npz')
        matrix = tmp['arr_0']
        comp3=matrix[2]
        
        mean_class=zeros(30)
        
        for i in range (0,29):
            #idxmasked=copy(self.idx)
            mask = (self.idx==i)
            a=mean(comp3[mask])
            mean_class[i]=a
        
        self.min_class=zeros(10)
        a = 0
        b = 0
        while True:
            if mean_class[a]==max(mean_class):
                    self.min_class[b]= a
                    mean_class[a]=-30
                    b=b+1
            if b==3:
                break
            if a==29:
                a=-1
            a=a+1
        
        r1=zeros((self.idx.shape), dtype=int)
        g1=zeros((self.idx.shape), dtype=int)
        b1=zeros((self.idx.shape), dtype=int)
        
        r1=r1+255
        g1=g1+255
        b1=b1+255
    
        try:
                num=load('cclass.npy')
        except:
                num=methods.color_class()
                save('cclass',num)
        
        for i in range(0,3):
                mask=(self.idx==self.min_class[i])
                r1[mask]=num[1,0]
                g1[mask]=num[1,1]
                b1[mask]=num[1,2]
        r1[0,0]=0
        g1[0,0]=0
        b1[0,0]=0
        r1[1,1]=255
        g1[1,1]=255
        b1[1,1]=255
        mode = misc.toimage(array([r1,g1,b1]))
        compRGB=path+'/auto.tif'
        mode.save(compRGB)
        self.loadFile(compRGB)
    
        self.Dialog = QtGui.QDialog()
        Dialog = auto_sl(self.Dialog)
        Dialog.text_auto.connect(self.get_value) 
        a=self.Dialog.exec_()
        
    def get_value(self, value):
        
        r1=zeros((self.idx.shape), dtype=int)
        g1=zeros((self.idx.shape), dtype=int)
        b1=zeros((self.idx.shape), dtype=int)
        
        r1=r1+255
        g1=g1+255
        b1=b1+255
        
        try:
                num=load('cclass.npy')
        except:
                num=methods.color_class()
                save('cclass',num)
        
        for i in range(0,int(value)):
                mask=(self.idx==self.min_class[i])
                r1[mask]=num[1,0]
                g1[mask]=num[1,1]
                b1[mask]=num[1,2]
        r1[0,0]=0
        g1[0,0]=0
        b1[0,0]=0
        r1[1,1]=255
        g1[1,1]=255
        b1[1,1]=255
        mode = misc.toimage(array([r1,g1,b1]))
        compRGB=path+'/auto.tif'
        mode.save(compRGB)
        self._mdiArea.closeActiveSubWindow()
        self.loadFile(compRGB)
        
    def pprc(self):
          
        self.svf='a'+self.svf[1:5]
        #print(self.svf)
        methods.pre_process(path)
        self._pprc.setEnabled(0)
    
    def mask(self):
        if os.path.isfile(path+'/cmatrix.npz') == True:
            reply = QtGui.QMessageBox.question(self, 'Mensaje', "Save changes to previous files?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                if self.sscale==1:
                    savsac = QtGui.QMessageBox.question(self, 'Mensaje', "Overlay scale?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if savsac == QtGui.QMessageBox.No:
                        self.sscale=0
                folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Output Directory"))
                fileList = os.listdir(path)
                for fileName in fileList:
                    if fileName.endswith('.tif')==True:
                        name=path+'/'+fileName
                        origname = fileName.replace(".tif", "")
                        savef=folder+'/'+origname+'_'+os.path.basename(self.fname)+'.tif'
                        os.system('cp '+name+' '+savef)
                        if self.sscale==1:
                            os.system('convert -gravity SouthEast '+savef+' scalers.png -composite '+savef)
                            
        os.system('touch .masking')
        fileList = os.listdir(path)
        for fileName in fileList:
            if fileName != 'cmatrix.npz':
                os.remove(path+'/'+fileName)
        self._mdiArea.closeAllSubWindows()
        os.system('python mask.py '+path)
        espera=0
        while (espera==0):
            try:
                with open('.masking'):
                    pass
            except:
                espera=1
        self.loadFile(path+'/masked.tif')
        matrix=load(path+'/cmatrix.npz')['arr_0']
        _,m,n=matrix.shape
        pre = Image.open(path+'/masked.tif')
        if m > n:
            x=400
            y=int((n*400)/m)
        elif m==n:
            x=400
            y=400
        elif m<n:
            y=400
            x=int((m*400)/n)
        pre = pre.resize((y,x),Image.ANTIALIAS)
        mini=path+'/mini.tif'
        pre.save(mini)
        minmatrix=methods.conversion(path,mini)
        minmatrixsv=path+'/minimatrix'
        savez(minmatrixsv,minmatrix)
      
    def aihs(self):
        Form = QtGui.QDialog()
        ui = satur.saturwidget()
        ui.setupUi(Form,path,self.rad)
        a=Form.exec_()
        #svf=methods.satur(path,fact,op1,self.svf,1,self.rad)
        if a==1:
            compRGB=path+'/Sat.tif'
            self.loadFile(compRGB)
            self.svf=self.svf[0:3]+'a'+self.svf[4:5]
    
            self._pprc.setEnabled(0)
    def aiter(self):
        Form = QtGui.QDialog()
        ui = satur.saturwidget()
        ui.setupUi(Form,path,self.rad)
        a=Form.exec_()
        #svf=methods.satur(path,fact,op1,self.svf,1,self.rad)
        if a==1:
            compRGB=path+'/Sat.tif'
            self.svf=self.svf[0:3]+'a'+self.svf[4:5]
        os.rename(path+'/cmatrix.npz',path+'/bck_cmatrix.npz')
        os.rename(path+'/minimatrix.npz',path+'/bck_minimatrix.npz')
        os.rename(path+'/smatrix.npz',path+'/cmatrix.npz')
        
        matrix=load(path+'/cmatrix.npz')['arr_0'] 
        _,m,n=matrix.shape
        archiv3= path+'/mini.tif'
        pre = Image.open(archiv3)
        if m > n:
            x=400
            y=int((n*400)/m)
        elif m==n:
            x=400
            y=400
        elif m<n:
            y=400
            x=int((m*400)/n)
        pre = pre.resize((y,x),Image.ANTIALIAS)
        pre.save(archiv3)
        minmatrix=methods.conversion(path,archiv3)
        minmatrixsv=path+'/minimatrix'
        savez(minmatrixsv,minmatrix)
        
        if os.path.isfile(path+'/pcamatrix.npz') == True:
            os.rename(path+'/pcamatrix.npz',path+'/bck_pcamatrix.npz')
            os.rename(path+'/pcadata.txt',path+'/bck_pcadata.txt')
        Form = QtGui.QDialog()
        ui = pca.pcawidget()
        ui.setupUi(Form,path)
        a=Form.exec_()
        if a==1:
            compRGB=path+'/compRGB.tif'
            comp1=path+'/comp1.tif'
            comp2=path+'/comp2.tif'
            comp3=path+'/comp3.tif'
            self.loadFile(compRGB)
            self.loadFile(comp1)
            self.loadFile(comp2)
            self.loadFile(comp3)
        if os.path.isfile(path+'/pcamatrix.npz') == True:
            self.svf= 'a'+self.svf[1:5]
        if os.path.isfile(path+'/alt_pcamatrix.npz') == True:
                self.svf= self.svf[0]+'a'+self.svf[2:5]
        self._pprc.setEnabled(0)
        self._greyband.setEnabled(1)
        
    
        os.rename(path+'/pcamatrix.npz',path+'/itermatrix.npz')
        os.rename(path+'/bck_pcadata.txt',path+'/pcadata.txt')
        os.rename(path+'/bck_pcamatrix.npz',path+'/pcamatrix.npz')
        os.rename(path+'/cmatrix.npz',path+'/smatrix.npz')
        os.rename(path+'/bck_cmatrix.npz',path+'/cmatrix.npz')
        os.rename(path+'/bck_minimatrix.npz',path+'/minimatrix.npz')

                
    def apca(self):
            Form = QtGui.QDialog()
            ui = pca.pcawidget()
            ui.setupUi(Form,path)
            a=Form.exec_()
            if a==1:
                compRGB=path+'/compRGB.tif'
                comp1=path+'/comp1.tif'
                comp2=path+'/comp2.tif'
                comp3=path+'/comp3.tif'
                self.loadFile(compRGB)
                self.loadFile(comp1)
                self.loadFile(comp2)
                self.loadFile(comp3)
            if os.path.isfile(path+'/pcamatrix.npz') == True:
                self.svf= 'a'+self.svf[1:5]
            if os.path.isfile(path+'/alt_pcamatrix.npz') == True:
                self.svf= self.svf[0]+'a'+self.svf[2:5]
            self._pprc.setEnabled(0)
            self._greyband.setEnabled(1) 

    def ads(self):
        
        Form = QtGui.QDialog()
        ui = ds.dswidget()
        ui.setupUi(Form,path)
        a=Form.exec_()
        print(a)
        if a==1:
            compRGB=path+'/dstr.tif'
            self.loadFile(compRGB)
            self.svf= self.svf[0:1]+'a'+self.svf[3:5]
            print (self.svf)
    
    def bm(self):
        """Handle the open action."""
        fileDialog = QtGui.QFileDialog(self)
        settings = QtCore.QSettings()
        fileDialog.setNameFilters(["Image Files (*.jpg *.png *.tif)","All Files (*)"])
        if not settings.contains(SETTING_FILEOPEN + "/state"):
            fileDialog.setDirectory(".")
        else:
            self.restoreDialogState(fileDialog, SETTING_FILEOPEN)
            fileDialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        if not fileDialog.exec_():
            return
        self.saveDialogState(fileDialog, SETTING_FILEOPEN)

        self.fname = fileDialog.selectedFiles()
    
        datalist=[('Method',[0,'PCA','Decorrelation Stretch','Saturation from 3rd component','K-Means']),]
        met=fedit(datalist, title="Select Method")
            
        Directory = str(QtGui.QFileDialog.getExistingDirectory(self, "Output Directory"))
        Directory= Directory.replace(' ','\ ')
        
        if met==[0]:
           
            datalist=[('1st component',False),('2nd component',False),('3rd component',False),('RGB composition',False),('Auto-enhacement',False),('Auto-contrast components',False),('Output PDF report',False),('RBG inversion',False),('R to component',[1,'1','2','3']),('G to component',[2,'1','2','3']),('B to component',[2,'1','2','3']),]
            sv1,sv2,sv3,sv4,op1,op2,op3,op4,RC,GC,BC=fedit(datalist, title= "PCA Options")
           
            for i in range(len(self.fname)):
                self.rad=8
                methods.pca(self.fname[i],self.rad,path,op1,op2,op3,op4,RC,GC,BC,self.svf,0)
                if sv1==True:
                    comp1=path+'/comp1.tif'
                    savef=Directory+'/pc1_'+os.path.basename(self.fname[i])
                    copy = 'cp '+comp1+' '+savef
                    print (copy)
                    os.system(copy)
                if sv2==True:
                    comp2=path+'/comp2.tif'
                    savef=Directory+'/pc2_'+os.path.basename(self.fname[i])
                    copy = 'cp '+comp2+' '+savef
                    os.system(copy)
                if sv3==True:
                    comp3=path+'/comp3.tif'
                    savef=Directory+'/pc3_'+os.path.basename(self.fname[i])
                    copy = 'cp '+comp3+' '+savef
                    os.system(copy)
                if sv3==True:
                    compRGB=path+'/compRGB.tif'
                    savef=Directory+'/FalseRGB_'+os.path.basename(self.fname[i])
                    copy = 'cp '+compRGB+' '+savef
                    os.system(copy)

        if met==[1]:
   
            datalist=[('Auto-enhacement',False),('Auto-contrast result',False),('Fixed offset',False),('Stretch Constant',50),('R to band',[0,'1','2','3']),('G to band',[1,'1','2','3']),('B to band',[2,'1','2','3']),]
            op1,op2,op3,SC,RC,GC,BC=fedit(datalist, title= "Decorrelation Stretch Options")
    
            for i in range(len(self.fname)):
                methods.stretch(self.fname[i],path,op1,op2,op3,SC,RC,GC,BC,self.svf,0)
                compRGB=path+'/dstr.tif'
                savef=Directory+'/DS_'+os.path.basename(self.fname[i])
                copy = 'cp '+compRGB+' '+savef
                os.system(copy)

        if met==[2]:

            datalist=[('Weighted value for 3rd component',100),('Equalization of 3rd component',False),]
            fact,op1=fedit(datalist, title= "Saturation Options")
            for i in range(len(self.fname)):
                methods.satur(self.fname,path,fact,op1,self.svf,0,self.rad)
                compRGB=path+'/compRGB.tif'
                savef=Directory+'/Sat_'+os.path.basename(self.fname[i])
                copy = 'cp '+compRGB+' '+savef
                os.system(copy)
    
    def akmeans(self):
                
        optionlist=[0, 'Original RGB image', 'PCA', 'Decorrelation Stretch', 'Saturation from 3rd component','Iterative analysis']
        if os.path.isfile(path+'/pcamatrix.npz') == True:
            optionlist.append('Preprocessed standard PCA')
        if os.path.isfile(path+'/alt_pcamatrix.npz') == True:
            optionlist.append('Preprocessed non-standard PCA')
        if os.path.isfile(path+'/dsmatrix.npz') == True:
            optionlist.append('Preprocessed Decorrelation')
        if os.path.isfile(path+'/smatrix.npz') == True:
            optionlist.append('Preprocessed Saturation')
        if os.path.isfile(path+'/itermatrix.npz') == True:
            optionlist.append('Preprocessed Iterative Analysis')
        ct=0
        contador=1
        while (ct==0):
            filefal=path+'/false_colour_'+str(contador)+'.tif'
            try:
                with open(filefal):
                    optionlist.append(filefal[-18:])
                    contador=contador+1
            except:
                ct=1

        datalist=[('Number of classes',15),('Processing Method',optionlist),]
        numb,op=fedit(datalist, title= "K-Means option")
        
        if op==0:
            idx,svf=methods.k_means(numb,'cmatrix',path,self.svf)
            #kk=Image.open(self.fname)
            print ('cmatrix')
            
        if op==1:
            self.apca()
            idx,svf=methods.k_means(numb,'pcamatrix',path,self.svf)
            print ('pcamatrix')
            
        if op==2:
            self.ads()
            idx,svf=methods.k_means(numb,'dsmatrix',path,self.svf)
            print ('dsmatrix')
            
        if op==3:
            self.aihs()
            idx,svf=methods.k_means(numb,'smatrix',path,self.svf)
            print ('smatrix')
        
        if op==4:
            self.aiter()
            idx,svf=methods.k_means(numb,'itermatrix',path,self.svf)
            print ('itermatrix')
            
        if op > 4:
                chosen=optionlist[op+1]
                if chosen=='Preprocessed standard PCA':
                    idx,svf=methods.k_means(numb,'pcamatrix',path,self.svf)
                    print ('pcamatrix')
                elif chosen=='Preprocessed non-standard PCA':
                    idx,svf=methods.k_means(numb,'alt_pcamatrix',path,self.svf)
                    print ('alt_pcamatrix')
                elif chosen=='Preprocessed Decorrelation':
                    idx,svf=methods.k_means(numb,'dsmatrix',path,self.svf)
                    print ('dsmatrix')
                elif chosen=='Preprocessed Saturation':
                    idx,svf=methods.k_means(numb,'smatrix',path,self.svf)
                    print ('smatrix')
                elif chosen=='Preprocessed Iterative Analysis':
                    idx,svf=methods.k_means(numb,'itermatrix',path,self.svf)
                    print ('itermatrix')
                
                
                if chosen[-4:]=='.tif':
                    from osgeo import gdal
                    filename = gdal.Open(path+'/'+chosen)
                    br=filename.GetRasterBand(1).ReadAsArray()
                    bg=filename.GetRasterBand(2).ReadAsArray()
                    bb=filename.GetRasterBand(3).ReadAsArray()

                    matrix = array([br,bg,bb],'f')
                    print ('falmatrix')
                    matrixsv=path+'/falmatrix'
                    savez(matrixsv,matrix)
                    idx,svf=methods.k_means(numb,'falmatrix',path,self.svf)
        
        fullname=path+'/cmatrix.npz'
        matrix = load(fullname)['arr_0'] 
        idxmasked=copy(matrix)
        mask = (idx==0)
        idxmasked[1][mask]=255
        
        mode=misc.toimage(idxmasked)
        kmeanclass = path+'/tmp_class.tif'
        mode.save(kmeanclass)
        self.loadFile(kmeanclass)
        
        self.Form = QtGui.QDialog()
        Form = kmeanwidget(self.Form,path,idx,self.fname)
        Form.textSaved.connect(self.get_order)
        a=self.Form.exec_()
             
    def get_order(self, message):
        
        if message=="normal":
            kmeanclass = path+'/tmp_class.tif'
            self._mdiArea.closeActiveSubWindow()
            self.loadFile(kmeanclass)
        if message=="apply":
            compRGB=path+'/kmeans.tif'
            self._mdiArea.closeActiveSubWindow()
            self.loadFile(compRGB)
        
    def cloudpca(self):
        fileDialog = QtGui.QFileDialog(self)
        settings = QtCore.QSettings()
        fileDialog.setNameFilters(["Image Files (*.xyz *.txt)"])
        if not settings.contains(SETTING_FILEOPEN + "/state"):
            fileDialog.setDirectory(".")
        else:
            self.restoreDialogState(fileDialog, SETTING_FILEOPEN)
        fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if not fileDialog.exec_():
            return
        self.saveDialogState(fileDialog, SETTING_FILEOPEN)

        self.cloudname = fileDialog.selectedFiles()[0]
        os.system('python cloud.py self.cloudname')
        
    def setscale(self):
        from formlayout import fedit
        datalist = [('Pixel size (mm)','1'),('Inverse', False)]
        optpix=fedit(datalist, title="Set the pixel size")
        pixsize=float(optpix[0])
        
        print ('size '+str(pixsize))
        os.system('convert scale.png -resize '+str(100*pixsize)+'% scalers.png')
        if optpix[1]==True:
            os.system('convert scalers.png -negate scalers.png')
        self.sscale=1
    
    def rocker(self):
        os.system('touch .masking')
        vuelta=1
        while (vuelta>0):
           os.system('python rocker_backup.py '+path)
           espera=0
           while (espera==0):
               try:
                   with open('.masking'):
                       pass
               except:
                   espera=1
           reply = QtGui.QMessageBox.question(self, 'Mensaje', "Edit another class?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
           if reply == QtGui.QMessageBox.No:
                vuelta=0
        self.loadFile(path+'/kmeans_edited.tif')
    
    def greyband(self):
        espera=0
        os.system('touch .clahing')
        os.system('python grayband2.py '+path)
        while (espera==0):
            try:
                with open ('.clahing'):
                    pass
            except:
                espera=1
        contador=1
        i=0
        while (i==0):
            file=path+'/false_colour_'+str(contador)+'.tif'
            try:
                with open(file):
                    contador=contador+1
            except:
                os.system('cp '+path+'/temp_col.tif '+file)
                os.system('rm '+path+'/temp_col.tif')
                i=1
        self.loadFile(file)
        
        
   
    def histograms(self):
        import matplotlib.pyplot as plt
        fig,((ax1,ax2,ax3),(ax4,ax5,ax6))=plt.subplots(ncols=3,nrows=2,figsize=(30,20))
        color=load(path+'/cmatrix.npz')['arr_0']
        ax1.hist(color[0][color[0]>1].flatten(),50,color='red')
        ax1.set_title('Red channel')
        ax1.set_xlim(0,255)
        ax2.hist(color[1][color[1]>1].flatten(),50,color='green')
        ax2.set_xlim(0,255)
        ax2.set_title('Green channel')
        ax3.set_xlim(0,255)
        ax3.hist(color[2][color[2]>1].flatten(),50,color='blue')
        ax3.set_title('Blue channel')
        try:
            compon=load(path+'/pcamatrix.npz')['arr_0']
            ax4.hist(compon[0].flatten(),50,color='gray')
            ax4.set_title('First component')
            ax5.hist(compon[1].flatten(),50,color='gray')
            ax5.set_title('Second component')
            ax6.hist(compon[2].flatten(),50,color='gray')
            ax6.set_title('Third component')
        except:
            pass
        plt.savefig('histograms.jpg')
        os.system('open histograms.jpg')
        
    def tracenoise(self):
        Form = QtGui.QDialog()
        ui = trfilter.trnoisewidget()
        ui.setupUi(Form,path)
        a=Form.exec_()
        
        if a==1:
            compRGB=path+'/dstr.tif'
            self.loadFile(compRGB)
            self.svf= self.svf[0:1]+'a'+self.svf[3:5]
            print (self.svf)

    def openNEF(self):
        """Handle the open action."""
        if os.path.isfile(path+'/cmatrix.npz') == True:
            reply = QtGui.QMessageBox.question(self, 'Mensaje', "Save changes?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Output Directory"))
                fileList = os.listdir(path)
                for fileName in fileList:
                    if fileName.endswith('.tif')==True:
                        if fileName <> 'mini.tif':
                            name=path+'/'+fileName
                            origname = fileName.replace(".tif", "")
                            savef=folder+'/'+origname+'_'+os.path.basename(self.fname)+'.tif'
                            copy = 'cp '+name+' '+savef
                            os.system(copy)
                        if fileName=='kmatrix.npz':
                            name=path+'/'+fileName
                            savef=folder+'/'+origname+'.dra'
                            os.system('cp '+name+' '+savef)
                        if fileName=='pcadata.txt':
                            name=path+'/'+fileName
                            savef=folder+'/'+origname+'_pcadata.txt'
                            os.system('cp '+name+' '+savef)
                        
            fileList = os.listdir(path)
            for fileName in fileList:
                os.remove(path+'/'+fileName)
            self._mdiArea.closeAllSubWindows()
        fileDialog = QtGui.QFileDialog(self)
        settings = QtCore.QSettings()
        fileDialog.setNameFilters(["Image Files (*.nef)",
                                   "All Files (*)"])
        if not settings.contains(SETTING_FILEOPEN + "/state"):
            fileDialog.setDirectory(".")
        else:
            self.restoreDialogState(fileDialog, SETTING_FILEOPEN)
        fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        if not fileDialog.exec_():
            return
        self.saveDialogState(fileDialog, SETTING_FILEOPEN)

        self.fname = fileDialog.selectedFiles()[0]
        w=os.path.basename(self.fname)

        nef = path+'/orignef.nef'
        self.fname= self.fname.replace(' ','\ ')
        copy = 'cp '+self.fname+' '+nef
        os.system(copy)
        
        convert2 = 'dcraw -j -W -T '+nef
        os.system(convert2)
        archiv2= path+'/orignef.tiff'
        archiv3= path+'/mini.tif'
        os.rename(archiv2,archiv3)
                
        convert ='dcraw -j -W -T -6 '+nef
        os.system(convert)
        archiv = path+'/orignef.tif'
        archiv1 = archiv+'f'
        os.rename(archiv1,archiv)
        self.fname=path+'/orignef.tif'
        
        self.loadFile(self.fname)

        matrix=methods.conversion(path,self.fname)
        matrixsv=path+'/cmatrix'
        savez(matrixsv,matrix)
        _,m,n=matrix.shape
        pre = Image.open(archiv3)
        if m > n:
            x=400
            y=int((n*400)/m)
        elif m==n:
            x=400
            y=400
        elif m<n:
            y=400
            x=int((m*400)/n)
        pre = pre.resize((y,x),Image.ANTIALIAS)
        pre.save(archiv3)
        minmatrix=methods.conversion(path,archiv3)
        minmatrixsv=path+'/minimatrix'
        savez(minmatrixsv,minmatrix)
        self.rad = 16
        self.svf='nnnnn'
        self.deactiv(1)
        
        
          
    @QtCore.pyqtSlot()
    def toggleScrollbars(self):
        """Toggle subwindow scrollbar visibility."""
        checked = self._showScrollbarsAct.isChecked()

        windows = self._mdiArea.subWindowList()
        for window in windows:
            child = window.widget()
            child.enableScrollBars(checked)

    @QtCore.pyqtSlot()
    def toggleStatusbar(self):
        """Toggle status bar visibility."""
        self.statusBar().setVisible(self._showStatusbarAct.isChecked())

    @QtCore.pyqtSlot()
    def about(self):
        """Display About dialog box."""
        QtGui.QMessageBox.about(self, "About MDI",
                "<b>MDI Image Viewer</b> demonstrates how to"
                "synchronize the panning and zooming of multiple image"
                "viewer windows using Qt.")

    @QtCore.pyqtSlot(QtGui.QMdiSubWindow)
    def subWindowActivated(self, window):
        """Handle |QMdiSubWindow| activated signal.

        :param |QMdiSubWindow| window: |QMdiSubWindow| that was just
                                       activated"""
        self.updateStatusBar()

    @QtCore.pyqtSlot(QtGui.QMdiSubWindow)
    def setActiveSubWindow(self, window):
        """Set active |QMdiSubWindow|.

        :param |QMdiSubWindow| window: |QMdiSubWindow| to activate """
        if window:
            self._mdiArea.setActiveSubWindow(window)

    # ------------------------------------------------------------------

    def loadFile(self, filename):
        """Load filename into new :class:`MdiChild` window.

        :param str filename: filename to load"""
        activeMdiChild = self.activeMdiChild
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        pixmap = QtGui.QPixmap(filename)
        QtGui.QApplication.restoreOverrideCursor()
        if (not pixmap or
            pixmap.width()==0 or pixmap.height==0):
            QtGui.QMessageBox.warning(self, APPNAME,
                                      "Cannot read file %s." % (filename,))
            self.updateRecentFileSettings(filename, delete=True)
            self.updateRecentFileActions()
            return

        child = self.createMdiChild(pixmap, filename)
        child.show()

        if activeMdiChild:
            if self._synchPanAct.isChecked():
                self.synchPan(activeMdiChild)
            if self._synchZoomAct.isChecked():
                self.synchZoom(activeMdiChild)

        self.updateRecentFileSettings(filename)
        self.updateRecentFileActions()

        self.statusBar().showMessage("File loaded", 2000)

    def updateStatusBar(self):
        """Update status bar."""
        self.statusBar().setVisible(self._showStatusbarAct.isChecked())
        imageViewer = self.activeMdiChild
        if not imageViewer:
            self._sbLabelName.setText("")
            self._sbLabelSize.setText("")
            self._sbLabelDimensions.setText("")
            self._sbLabelDate.setText("")
            self._sbLabelZoom.setText("")

            self._sbLabelSize.hide()
            self._sbLabelDimensions.hide()
            self._sbLabelDate.hide()
            self._sbLabelZoom.hide()
            return

        filename = imageViewer.currentFile
        self._sbLabelName.setText(" %s " % filename)

        fi = QtCore.QFileInfo(filename)
        size = fi.size()
        fmt = " %.1f %s "
        if size > 1024*1024*1024:
            unit = "MB"
            size /= 1024*1024*1024
        elif size > 1024*1024:
            unit = "MB"
            size /= 1024*1024
        elif size > 1024:
            unit = "KB"
            size /= 1024
        else:
            unit = "Bytes"
            fmt = " %d %s "
        self._sbLabelSize.setText(fmt % (size, unit))

        pixmap = imageViewer.pixmap
        self._sbLabelDimensions.setText(" %dx%dx%d " %
                                        (pixmap.width(),
                                         pixmap.height(),
                                         pixmap.depth()))

        self._sbLabelDate.setText(
            " %s " %
            fi.lastModified().toString(QtCore.Qt.SystemLocaleShortDate))
        self._sbLabelZoom.setText(" %0.f%% " % (imageViewer.zoomFactor*100,))

        self._sbLabelSize.show()
        self._sbLabelDimensions.show()
        self._sbLabelDate.show()
        self._sbLabelZoom.show()

    def createMdiChild(self, pixmap, filename):
        """Create new :class:`MdiChild` for pixmap.

        :param pixmap: |QPixmap| to display in :class:`MdiChild`
        :type pixmap: |QPixmap| or None
        :param filename: |QPixmap| filename
        :type filename: str or None
        :rtype: :class:`MdiChild`"""
        child = MdiChild(pixmap,filename,"")

        ##Para que aparezca nombre child = MdiChild(pixmap,filename,"Child %d" % (len(self._mdiArea.subWindowList())+1))
        child.enableScrollBars(self._showScrollbarsAct.isChecked())
        window = self._mdiArea.addSubWindow(child)

        child.scrollChanged.connect(self.panChanged)
        child.transformChanged.connect(self.zoomChanged)

        return child
    
    

    def switchLayoutDirection(self):
        """Switch MDI subwindow layout direction."""
        if self.layoutDirection() == QtCore.Qt.LeftToRight:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.LeftToRig)           

    def capture1(self):
        if os.path.isfile(path+'/cmatrix.npz') == True:
            reply = QtGui.QMessageBox.question(self, 'Mensaje', "Save changes?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                folder = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Output Directory"))
                fileList = os.listdir(path)
                for fileName in fileList:
                    if fileName.endswith('.tif')==True:
                        name=path+'/'+fileName
                        origname = fileName.replace(".tif", "")
                        savef=folder+'/'+origname+'_'+os.path.basename(self.fname)+'.tif'
                        copy = 'cp '+name+' '+savef
                        os.system(copy)
            fileList = os.listdir(path)
            for fileName in fileList:
                os.remove(path+'/'+fileName)
            self._mdiArea.closeAllSubWindows()
           
        methods.capture_nikon(path)
        nef = path+'/orignef.nef'
                
        convert2 = 'dcraw -j -W -T '+nef
        os.system(convert2)
        archiv2= path+'/orignef.tiff'
        archiv3= path+'/mini.tif'
        os.rename(archiv2,archiv3)
                
        convert ='dcraw -j -W -T -6 '+nef
        os.system(convert)
        archiv = path+'/orignef.tif'
        archiv1 = archiv+'f'
        os.rename(archiv1,archiv)
        self.fname=path+'/orignef.tif'
        
        self.loadFile(self.fname)

        matrix=methods.conversion(path,self.fname)
        matrixsv=path+'/cmatrix'
        savez(matrixsv,matrix)
        _,m,n=matrix.shape
        pre = Image.open(archiv3)
        if m > n:
            x=400
            y=int((n*400)/m)
        elif m==n:
            x=400
            y=400
        elif m<n:
            y=400
            x=int((m*400)/n)
        pre = pre.resize((y,x),Image.ANTIALIAS)
        pre.save(archiv3)
        minmatrix=methods.conversion(path,archiv3)
        minmatrixsv=path+'/minimatrix'
        savez(minmatrixsv,minmatrix)
        self.rad = 16
        self.sscale=0
        self.svf='nnnnn'
        self.deactiv(1)

                 
    def bar(self):
        
        self.pbar = QtGui.QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        
        self.btn = QtGui.QPushButton('Start', self)
        self.btn.move(40, 80)
        self.btn.clicked.connect(self.doAction)
        
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QtGui.QProgressBar')
        self.show()
        

    def synchPan(self, fromViewer):
        """Synch panning of all subwindowws to the same as *fromViewer*.

        :param fromViewer: :class:`MdiChild` that initiated synching"""
        assert isinstance(fromViewer, MdiChild)
        if not fromViewer:
            return
        if self._handlingScrollChangedSignal:
            return
        self._handlingScrollChangedSignal = True

        newState = fromViewer.scrollState
        changedWindow = fromViewer.parent()
        windows = self._mdiArea.subWindowList()
        for window in windows:
            if window != changedWindow:
                window.widget().scrollState = newState
        self._handlingScrollChangedSignal = False

    def synchZoom(self, fromViewer):
        """Synch zoom of all subwindowws to the same as *fromViewer*.

        :param fromViewer: :class:`MdiChild` that initiated synching"""
        if not fromViewer:
            return
        newZoomFactor = fromViewer.zoomFactor
        changedWindow = fromViewer.parent()
        windows = self._mdiArea.subWindowList()
        for window in windows:
            if window != changedWindow:
                window.widget().zoomFactor = newZoomFactor

    # ------------------------------------------------------------------

    def saveDialogState(self, dialog, groupName):
        """Save dialog state, position & size.

        :param |QDialog| dialog: dialog to save state of
        :param str groupName: |QSettings| group name"""
        assert isinstance(dialog, QtGui.QDialog)

        settings = QtCore.QSettings()
        settings.beginGroup(groupName)

        settings.setValue('state', dialog.saveState())
        settings.setValue('geometry', dialog.saveGeometry())
        settings.setValue('filter', dialog.selectedNameFilter())

        settings.endGroup()

    def restoreDialogState(self, dialog, groupName):
        """Restore dialog state, position & size.

        :param str groupName: |QSettings| group name"""
        assert isinstance(dialog, QtGui.QDialog)

        settings = QtCore.QSettings()
        settings.beginGroup(groupName)

        dialog.restoreState(settings.value('state'))
        dialog.restoreGeometry(settings.value('geometry'))
        dialog.selectNameFilter(settings.value('filter', ""))

        settings.endGroup()

    def writeSettings(self):
        """Write application settings."""
        settings = QtCore.QSettings()
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
        settings.setValue('windowgeometry', self.saveGeometry())
        settings.setValue('windowstate', self.saveState())

        settings.setValue(SETTING_SCROLLBARS,
                          self._showScrollbarsAct.isChecked())
        settings.setValue(SETTING_STATUSBAR,
                          self._showStatusbarAct.isChecked())
        settings.setValue(SETTING_SYNCHZOOM,
                          self._synchZoomAct.isChecked())
        settings.setValue(SETTING_SYNCHPAN,
                          self._synchPanAct.isChecked())

    def readSettings(self):
        """Read application settings."""
        settings = QtCore.QSettings()
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)
        if settings.contains('windowgeometry'):
            self.restoreGeometry(settings.value('windowgeometry'))
        if settings.contains('windowstate'):
            self.restoreState(settings.value('windowstate'))

        self._showScrollbarsAct.setChecked(
            toBool(settings.value(SETTING_SCROLLBARS, True)))
        self._showStatusbarAct.setChecked(
            toBool(settings.value(SETTING_STATUSBAR, True)))
        self._synchZoomAct.setChecked(
            toBool(settings.value(SETTING_SYNCHZOOM, True)))
        self._synchPanAct.setChecked(
            toBool(settings.value(SETTING_SYNCHPAN, True)))

    def updateRecentFileSettings(self, filename, delete=False):
        """Update recent file list setting.

        :param str filename: filename to add or remove from recent file
                             list
        :param bool delete: if True then filename removed, otherwise added"""
        settings = QtCore.QSettings()
        files = list(settings.value(SETTING_RECENTFILELIST, []))

        try:
            files.remove(filename)
        except ValueError:
            pass

        if not delete:
            files.insert(0, filename)
        del files[MDIImageViewerWindow.MaxRecentFiles:]

        settings.setValue(SETTING_RECENTFILELIST, files)


# ====================================================================

def main():
    """Run MDI Image Viewer application."""

    app = QtGui.QApplication(sys.argv)
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
    app.setOrganizationName(COMPANY)
    app.setOrganizationDomain(DOMAIN)
    app.setApplicationName(APPNAME)
    app.setWindowIcon(QtGui.QIcon("images/icono.png"))

    mainWin = MDIImageViewerWindow()
    mainWin.setWindowTitle(APPNAME)

    mainWin.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    path = tempfile.mkdtemp()
    main()

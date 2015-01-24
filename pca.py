# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created: Sun Jul  7 16:02:00 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtCore, QtGui
from PIL import ImageQt
from numpy import *
from scipy import linalg as ln
from scipy import misc
import functools,methods,os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


  
def actual(self):
    self.mode1,self.mode2,self.mode3,self.mode4=pca(self.path,self.op1,self.op2,self.op4,self.RC,self.GC,self.BC)
    if str(self.show.currentText()) == 'RGB Composition':
        QtImage1 = ImageQt.ImageQt(self.mode4)
    if str(self.show.currentText()) == 'Component 1':
        QtImage1 = ImageQt.ImageQt(self.mode1)
    if str(self.show.currentText()) == 'Component 2':
        QtImage1 = ImageQt.ImageQt(self.mode2)
    if str(self.show.currentText()) == 'Component 3':
        QtImage1 = ImageQt.ImageQt(self.mode3)
    QtImage2 = QtGui.QImage(QtImage1)
    self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
    
def showch(self,show):
    if show==0:
        QtImage1 = ImageQt.ImageQt(self.mode3)
    elif show==1:
        QtImage1 = ImageQt.ImageQt(self.mode2)
    elif show==2:
        QtImage1 = ImageQt.ImageQt(self.mode1)
    elif show==3:
        QtImage1 = ImageQt.ImageQt(self.mode4)
    QtImage2 = QtGui.QImage(QtImage1)
    self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
    
def R_comboch(self,R_combo):
    if R_combo==0: self.RC=0
    if R_combo==1: self.RC=1
    if R_combo==2: self.RC=2
    showch(self,3)
    self.show.setCurrentIndex(3)
    actual(self)
    
def G_comboch(self,G_combo):
    if G_combo==0: self.GC=0
    if G_combo==1: self.GC=1
    if G_combo==2: self.GC=2
    showch(self,3)
    self.show.setCurrentIndex(3)
    actual(self)

def B_comboch(self,B_combo):
    if B_combo==0: self.BC=0
    if B_combo==1: self.BC=1
    if B_combo==2: self.BC=2
    showch(self,3)
    self.show.setCurrentIndex(3)
    actual(self)

def autenhch(self):
    if self.check_autenh.isChecked():
        self.op1=True
    else:
        self.op1=False
    actual(self)

def rbgch(self):
    if self.check_rbg.isChecked():
        self.op4=True
    else:
        self.op4=False
    actual(self)
    
def contch(self):
    if self.check_cont.isChecked():
        self.op2=True
    else:
        self.op2=False
    actual(self)

def pca(path,op1,op2,op4,RC,GC,BC):
    fullname=path+'/minimatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
    m,n=matrix[0].shape
    if op4== True:
        immatrix = array([matrix[0].flatten(),matrix[2].flatten(),matrix[1].flatten()],'f')
    else:
        immatrix = array([matrix[0].flatten(),matrix[1].flatten(),matrix[2].flatten()],'f')
      #Pasa la opcion 1, ecualizar automaticamente la imagen
    if op1== True:
        immatrix,cdf=methods.histeq(immatrix)

    M = cov(immatrix)
    e,EV = ln.eigh(M)
    tmp = dot(immatrix.T,EV).T #this is the compact trick
    tmp2 = tmp[::-1].reshape(3,m,n) #ordenar el producto de la matriz por los autovectores
  
    if op2== True:
        V,cdf=methods.histeq(tmp2)
    else:
        V=tmp2
    mode2 = misc.toimage(array([V[1],V[1],V[1]]))    
    #V[2][V[2]<V[2].min()*20]=0
    print (V[2].max()*80)/100
   # V[2][V[2]>(V[2].max()*50)/100]=(V[2].max()*50)/100
    mode1 = misc.toimage(array([V[0],V[0],V[0]]))
    
    mode3 = misc.toimage(array([V[2],V[2],V[2]]))

    if RC == 0: RS=V[0]
    if RC == 1: RS=V[1]
    if RC == 2: RS=V[2]
    if GC == 0: GS=V[0]
    if GC == 1: GS=V[1]
    if GC == 2: GS=V[2]
    if BC == 0: BS=V[0]
    if BC == 1: BS=V[1]
    if BC == 2: BS=V[2]
  
    mode4 = misc.toimage(array([RS,GS,BS]))
  
    return mode1,mode2,mode3,mode4

class pcawidget(object):
    
    def applied(self,Form):
        if os.path.isfile(self.path+'/pcamatrix.npz') == True: #comprueba que no exista la matriz de PCA en el disco duro
            filecheck='annnn'
            print('clo')
        else:
            filecheck='nnnnn'
        methods.pca('X',8,self.path,self.op1,self.op2,False,self.op4,self.RC,self.GC,self.BC,filecheck,1)
        return Form.accept()
    
    def setupUi(self, Form,path):
        Form.resize(471, 552)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        #Form.setModal(True)
        Form.setMinimumSize(QtCore.QSize(471, 552))
        #Form.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../Dropbox/PyDRA/scripts Python/MDIImageViewer-master/images/icono.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.pic = QtGui.QLabel(Form)
        self.pic.setGeometry(QtCore.QRect(10, 10, 451, 411))
        self.pic.setObjectName(_fromUtf8("graphicsView"))
        self.show = QtGui.QComboBox(Form)
        self.show.setGeometry(QtCore.QRect(10, 430, 451, 26))
        self.show.setObjectName(_fromUtf8("comboBox"))
        self.show.addItem(_fromUtf8(""))
        self.show.addItem(_fromUtf8(""))
        self.show.addItem(_fromUtf8(""))
        self.show.addItem(_fromUtf8(""))
        self.widget = QtGui.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(10, 490, 451, 51))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.splitter_2 = QtGui.QSplitter(self.widget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.widget1 = QtGui.QWidget(self.splitter_2)
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout = QtGui.QGridLayout(self.widget1)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.widget1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.B_combo = QtGui.QComboBox(self.widget1)
        self.B_combo.setObjectName(_fromUtf8("B_combo"))
        self.B_combo.addItem(_fromUtf8(""))
        self.B_combo.addItem(_fromUtf8(""))
        self.B_combo.addItem(_fromUtf8(""))
        self.B_combo.setCurrentIndex(0)
        self.gridLayout.addWidget(self.B_combo, 1, 2, 1, 1)
        self.R_combo = QtGui.QComboBox(self.widget1)
        self.R_combo.setObjectName(_fromUtf8("R_combo"))
        self.R_combo.addItem(_fromUtf8(""))
        self.R_combo.addItem(_fromUtf8(""))
        self.R_combo.addItem(_fromUtf8(""))
        self.R_combo.setCurrentIndex(2)
        self.gridLayout.addWidget(self.R_combo, 1, 0, 1, 1)
        self.G_combo = QtGui.QComboBox(self.widget1)
        self.G_combo.setObjectName(_fromUtf8("G_combo"))
        self.G_combo.addItem(_fromUtf8(""))
        self.G_combo.addItem(_fromUtf8(""))
        self.G_combo.addItem(_fromUtf8(""))
        self.G_combo.setCurrentIndex(2)
        self.gridLayout.addWidget(self.G_combo, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget1)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.horizontalLayout_2.addWidget(self.splitter_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.butt_cancel = QtGui.QPushButton(self.widget)
        self.butt_cancel.setObjectName(_fromUtf8("butt_cancel"))
        self.verticalLayout.addWidget(self.butt_cancel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.widget2 = QtGui.QWidget(Form)
        self.widget2.setGeometry(QtCore.QRect(10, 460, 450, 20))
        self.widget2.setObjectName(_fromUtf8("widget2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.check_rbg = QtGui.QCheckBox(self.widget2)
        self.check_rbg.setObjectName(_fromUtf8("check_rbg"))
        self.horizontalLayout.addWidget(self.check_rbg)
        self.check_cont = QtGui.QCheckBox(self.widget2)
        self.check_cont.setObjectName(_fromUtf8("check_cont"))
        self.horizontalLayout.addWidget(self.check_cont)
        self.check_autenh = QtGui.QCheckBox(self.widget2)
        self.check_autenh.setObjectName(_fromUtf8("check_autenh"))
        self.horizontalLayout.addWidget(self.check_autenh)
        
        self.path=path
        self.op1=False
        self.op2=False
        self.op4=False
        self.RC=2
        self.GC=2
        self.BC=1
        
        self.show.activated.connect(functools.partial(showch, self))
        self.R_combo.activated.connect(functools.partial(R_comboch, self))
        self.G_combo.activated.connect(functools.partial(G_comboch, self))
        self.B_combo.activated.connect(functools.partial(B_comboch, self))
        self.check_autenh.stateChanged.connect(functools.partial(autenhch, self))
        self.check_rbg.stateChanged.connect(functools.partial(rbgch, self))
        self.check_cont.stateChanged.connect(functools.partial(contch, self))
        self.pushButton.clicked.connect(functools.partial(self.applied, Form))
        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.applied(Form))
        QtCore.QObject.connect(self.butt_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.reject)

        
        self.mode1,self.mode2,self.mode3,self.mode4=pca(self.path,self.op1,self.op2,self.op4,self.RC,self.GC,self.BC)
        
        QtImage1 = ImageQt.ImageQt(self.mode3)
        QtImage2 = QtGui.QImage(QtImage1)
        self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "PCA Processing", None, QtGui.QApplication.UnicodeUTF8))
        self.show.setItemText(0, QtGui.QApplication.translate("Form", "Component 3", None, QtGui.QApplication.UnicodeUTF8))
        self.show.setItemText(1, QtGui.QApplication.translate("Form", "Component 2", None, QtGui.QApplication.UnicodeUTF8))
        self.show.setItemText(2, QtGui.QApplication.translate("Form", "Component 1", None, QtGui.QApplication.UnicodeUTF8))
        self.show.setItemText(3, QtGui.QApplication.translate("Form", "RGB Composition", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "R channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "G channel", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "B channel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.butt_cancel.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.check_rbg.setText(QtGui.QApplication.translate("Form", "RBG inversion", None, QtGui.QApplication.UnicodeUTF8))
        self.check_cont.setText(QtGui.QApplication.translate("Form", "Auto-contrast components", None, QtGui.QApplication.UnicodeUTF8))
        self.check_autenh.setText(QtGui.QApplication.translate("Form", "Auto-enhacement", None, QtGui.QApplication.UnicodeUTF8))

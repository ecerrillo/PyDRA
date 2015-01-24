# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled2.ui'
#
# Created: Fri Jul 12 09:06:35 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PIL import ImageQt
from skimage import color
from numpy import *
from scipy import linalg as ln
from scipy import misc
import functools,methods,os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def actual(self):
    self.mode1=satur(self.path,self.fact,self.op1,self.rad)
    QtImage1 = ImageQt.ImageQt(self.mode1)
    QtImage2 = QtGui.QImage(QtImage1)
    self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))

def equalizch(self):
    if self.equaliz.isChecked():
        self.op1=True
    else:
        self.op1=False
    actual(self)

def weightch(self,value):
    self.fact=value
    actual(self)

def satur(path,fact,op1,rad):
    fullname=path+'/minimatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
    immatrix = array([matrix[0].flatten(),matrix[1].flatten(),matrix[2].flatten()],'f')
    
    if rad==8:
      rgbmatrix=(matrix.T)/255.0
    elif rad==16:
      rgbmatrix=(matrix.T)/65536.0
    h,s,v=(color.rgb2hsv(rgbmatrix)).T
    m,n = matrix[0].shape
    M = cov(immatrix)
    e,EV = ln.eigh(M)
    tmp = dot(immatrix.T,EV).T #this is the compact trick
    tmp2 = tmp[::-1].reshape(3,m,n) 
    fact=fact*1.0
    if op1==True:
      tmp2[2],_=methods.histeq(tmp2[2])
    splus3 =((tmp2[2]/fact))+(s)
    splus4 = splus3/amax(splus3)

    hsvmatrix=array([h,splus4,v]).T
    r,g,b=(color.hsv2rgb(hsvmatrix)).T
    fin = array([r,g,b])
    mode1 = misc.toimage(fin)
    return mode1
    

class saturwidget(object):
    def applied(self,Form):
      if os.path.isfile(self.path+'/pcamatrix.npz') == True: #comprueba que no exista la matriz de PCA en el disco duro
          filecheck='annnn'
      else:
          filecheck='nnnnn'
      methods.satur(self.path,self.fact,self.op1,filecheck,1,self.rad)
      return Form.accept()
    def setupUi(self, Form, path, rad):
        Form.resize(471, 552)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        #Form.setModal(True)
        Form.setMinimumSize(QtCore.QSize(471, 552))
        Form.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../Dropbox/PyDRA/scripts Python/MDIImageViewer-master/images/icono.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.pic = QtGui.QLabel(Form)
        self.pic.setGeometry(QtCore.QRect(10, 10, 451, 411))
        self.pic.setObjectName(_fromUtf8("graphicsView"))
        self.layoutWidget = QtGui.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(370, 460, 91, 68))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.butt_cancel = QtGui.QPushButton(self.layoutWidget)
        self.butt_cancel.setObjectName(_fromUtf8("butt_cancel"))
        self.verticalLayout.addWidget(self.butt_cancel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.weight = QtGui.QSlider(Form)
        self.weight.setGeometry(QtCore.QRect(20, 480, 271, 22))
        self.weight.setMaximum(500)
        self.weight.setMinimum(1)
        self.weight.setSingleStep(10)
        self.weight.setPageStep(10)
        self.weight.setOrientation(QtCore.Qt.Horizontal)
        self.weight.setTickPosition(QtGui.QSlider.TicksBelow)
        self.weight.setTickInterval(50)
        self.weight.setObjectName(_fromUtf8("weight"))
        self.equaliz = QtGui.QCheckBox(Form)
        self.equaliz.setGeometry(QtCore.QRect(20, 430, 221, 20))
        self.equaliz.setObjectName(_fromUtf8("equaliz"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 460, 241, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 510, 241, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.weight_2 = QtGui.QSlider(Form)
        self.weight_2.setGeometry(QtCore.QRect(20, 530, 271, 22))
        self.weight_2.setMaximum(1000)
        self.weight_2.setSingleStep(25)
        self.weight_2.setPageStep(10)
        self.weight_2.setOrientation(QtCore.Qt.Horizontal)
        self.weight_2.setTickPosition(QtGui.QSlider.TicksBelow)
        self.weight_2.setTickInterval(50)
        self.weight_2.setObjectName(_fromUtf8("weight_2"))
        
        self.path=path
        self.rad=rad
        self.op1=False
        self.fact=1
        
        self.equaliz.stateChanged.connect(functools.partial(equalizch, self))
        self.weight.valueChanged.connect(functools.partial(weightch, self))
        self.pushButton.clicked.connect(functools.partial(self.applied, Form))
        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.applied(Form))
        QtCore.QObject.connect(self.butt_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.reject)
        
        self.mode1=satur(self.path,self.fact,self.op1,self.rad)
        
        QtImage1 = ImageQt.ImageQt(self.mode1)
        QtImage2 = QtGui.QImage(QtImage1)
        self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
        
        self.retranslateUi(Form)
        
        QtCore.QMetaObject.connectSlotsByName(Form)
        QtCore.QObject.connect(self.butt_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.reject)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Saturation Processing", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.butt_cancel.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.equaliz.setText(QtGui.QApplication.translate("Form", "Equalization of 3rd component", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Weighted value for the 3rd component", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Correction of blue tones", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())


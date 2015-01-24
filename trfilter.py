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

def pasos(self):
    a=0
    m=0
    corte=90
    while(a==0):
        labeled, nr_objects = ndimage.label(self.z2)
        if m==0:
            max=nr_objects
            m=1
        perc=(nr_objects*100.0)/max
        sizes = ndimage.sum(self.z2,labeled,range(1,nr_objects+1)) 
        
        map = where(sizes==sizes.max())[0] + 1 
        mip = where(sizes==sizes.min())[0] + 1
        
        max_index = zeros(nr_objects + 1, uint8)
        max_index[map] = 1
        max_feature = max_index[labeled]
        
        min_index = zeros(nr_objects + 1, uint8)
        min_index[mip] = 1
        min_feature = min_index[labeled]    
        
        self.z2[min_feature==1] = 0
        self.z3[max_feature==1] = 0
        if perc < corte:
            print perc,nr_objects
            if corte > 10:
              corte = corte - 10
            elif corte < 10:
              corte = corte - 1                
            s = raw_input('¿Seguir? (s/n) ')
            if s=='n': a=1

def actual(self):
    self.mode1 = misc.toimage(self.z2)
    QtImage1 = ImageQt.ImageQt(self.mode1)
    QtImage2 = QtGui.QImage(QtImage1)
    self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))

def aisle(self,numb):
    lista=[]
    count=0
    for i in self.clases:
        if i==numb:
            lista.append(count)
        count=count+1
    
    self.z2=zeros(self.c.shape, dtype=int)    
    self.z3=zeros(self.c.shape, dtype=int)  
    self.z3=self.z3+255
    
    for i in lista:
       self.z2[c==i]=255
       
def reset(self):
    print

class trnoisewidget(object):
    def applied(self,Form):
        return Form.accept()
    def setupUi(self, Form, path):
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
        if os.path.isfile(self.path+'/kmatrix.npz') == False: #comprueba que no exista la matriz de PCA en el disco duro
          return Form.reject()
         
        self.filename=path+'/kmatrix.npz'
        self.a=load(self.filename)['arr_0']
        self.clases = load(self.filename)['arr_1']
        self.c=load(self.filename)['arr_2']
        self.lista=[]
        count=0
        for i in self.clases:
            if i==1:
                self.lista.append(count)
                count=count+1
        
        self.z2=zeros(self.c.shape, dtype=int)    
        self.z3=zeros(self.c.shape, dtype=int)  
        self.z3=self.z3+255
    
        for i in self.lista:
           self.z2[self.c==i]=255
        
        self.equaliz.stateChanged.connect(functools.partial(equalizch, self))
        self.weight.valueChanged.connect(functools.partial(weightch, self))
        self.pushButton.clicked.connect(functools.partial(self.applied, Form))
        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.applied(Form))
        QtCore.QObject.connect(self.butt_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.reject)
        
        self.mode1=misc.toimage(self.z2)
        
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


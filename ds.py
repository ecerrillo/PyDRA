# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created: Sun Jul  7 16:02:00 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtCore, QtGui
from PIL import ImageQt,ImageOps
from numpy import *
from scipy import linalg as ln
from skimage import color
from scipy import misc
import functools,methods

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def actual(self):
    self.mode1=ds(self.path,self.op1,self.op2,self.op3,self.op4,self.op5,self.huecorrec,self.SC,self.RC,self.GC,self.BC)
    QtImage1 = ImageQt.ImageQt(self.mode1)
    QtImage2 = QtGui.QImage(QtImage1)
    self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
    
def R_comboch(self,R_combo):
    if R_combo==0: self.RC=0
    if R_combo==1: self.RC=1
    if R_combo==2: self.RC=2
    actual(self)
    
def G_comboch(self,G_combo):
    if G_combo==0: self.GC=1
    if G_combo==1: self.GC=0
    if G_combo==2: self.GC=2
    actual(self)

def B_comboch(self,B_combo):
    if B_combo==0: self.BC=2
    if B_combo==1: self.BC=1
    if B_combo==2: self.BC=0
    actual(self)

def autenhch(self):
    if self.check_autenh.isChecked():
        self.op1=True
    else:
        self.op1=False
    actual(self)

def fixedch(self):
    if self.check_fixed.isChecked():
        self.op3=True
    else:
        self.op3=False
    actual(self)
    
def contch(self):
    if self.check_cont.isChecked():
        self.op2=True
    else:
        self.op2=False
    actual(self)

def saturch(self):
    if self.check_satur.isChecked():
        self.op4=True
    else:
        self.op4=False
    actual(self)

def intench(self):
    if self.check_inten.isChecked():
        self.op5=True
    else:
        self.op5=False
    actual(self)

def stretch(self,value):
    self.SC=value
    actual(self)

def hue_trch(self,value):
    self.huecorrec=value
    actual(self)

def ds(path,op1,op2,op3,op4,op5,huecorrec,SC,RC,GC,BC):
   
    fullname=path+'/minimatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
    
    #Pasa la opcion 1, ecualizar automaticamente la imagen
    if op1== True:
        tempmatrix,_=methods.histeq(matrix)
    else:
        tempmatrix=matrix
    
    _,m,n=tempmatrix.shape
    
    a_medias = zeros(tempmatrix.shape)
    for i in range (0,3):
            a_medias[i]=(tempmatrix[i]-mean(tempmatrix[i]))/std(tempmatrix[i]) #normalizacion con desv std

    immatrix=array([a_medias[0].flatten(),a_medias[1].flatten(),a_medias[2].flatten()]) #descomponiendo bandas
    
    M = corrcoef(immatrix) #matriz de correlaciones
    e,EV = ln.eigh(M)     #autovalores y autovectores
    tmp = dot(immatrix.T,EV).T #aplicar transformacion a PCA

    
    c=array([tmp[0].reshape(m,n).T,tmp[1].reshape(m,n).T,tmp[2].reshape(m,n).T]).T #vuelta a la matriz de imagen
    
    s_matrix=zeros((3,3),'f')  #creando la matriz para el stretch (whitening)
    for i in range (0,3):
            s_matrix[i,i]=1/sqrt(e[i])
    
    d=dot(c,s_matrix) #aplicar transformacion del stretch
    e=dot(d,EV.T)  #aplicando la transformacion inversa
    f=zeros((3,3)) #matriz diagonal con la desviación estandar
    for i in range(0,3):
            #f[i,i]=std(tempmatrix[i])
            f[i,i]=SC
    g=dot(e,f)    #aplicando la matriz diagonal
    
    h=zeros(g.shape) #aplicando offset
    
    if op3==True:
            for i in range(0,3):
                h[:,:,i]=g[:,:,i]+128
    else:   
            for i in range(0,3):
                h[:,:,i]=g[:,:,i]+mean(matrix[i])
    
    str4=empty_like(h)

    str4[:,:,0] = h[:,:,RC]
    str4[:,:,1] = h[:,:,GC]
    str4[:,:,2] = h[:,:,BC]

    if op4==False and op5==False and huecorrec==0:
        pass
    else:    
        hue,s,v=(color.rgb2hsv(str4/255.0)).T
    
        if op4 ==True:
            sst=(s-s.min())/s.max()
        else:
            sst=s
    
        if op5 ==True:
            vst=(v-v.min())/v.max()
        else:
            vst=v
    
        if huecorrec > 0:
            hue = hue + (huecorrec/100.0)
            mask = (hue > 1)
            hue[mask]=hue[mask]-(huecorrec/100.0)
        else:
            hue=hue
             
        hsvmatrix=array([hue,sst,vst]).T
    
        r,g,b=(color.hsv2rgb(hsvmatrix)).T
    
        str4=array([r.T,g.T,b.T])
    
    #Pasa la opcion 2, ecualizar automaticamente la imagen
    if op2== True:
        mode1 = ImageOps.equalize(misc.toimage(str4))
    else:
        mode1 = misc.toimage(str4)
    return mode1


class dswidget(object):
    def applied(self,Form):
        methods.stretch('X',self.path,self.op1,self.op2,self.op3,self.op4,self.op5,self.huecorrec,self.SC,self.RC,self.GC,self.BC,1)
        return Form.accept()
    def advanced(self,Form):
        if self.adv == 0:
            self.advButton.setText(QtGui.QApplication.translate("Form", "Standard", None, QtGui.QApplication.UnicodeUTF8))
            Form.setMinimumSize(QtCore.QSize(471, 700))
            self.adv = 1
        elif self.adv == 1:
            self.advButton.setText(QtGui.QApplication.translate("Form", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
            Form.setMinimumSize(QtCore.QSize(471, 590))
            Form.resize(471, 590)
            self.op4=False
            self.op5=False
            self.huecorrec=0
            self.adv = 0
            
        
    def setupUi(self, Form,path):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(471, 590)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(471,590))
        Form.setFocusPolicy(QtCore.Qt.ClickFocus)
        #Form.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../Dropbox/PyDRA/scripts Python/MDIImageViewer-master/images/icono.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.pic = QtGui.QLabel(Form)
        self.pic.setGeometry(QtCore.QRect(10, 10, 451, 411))
        self.pic.setObjectName(_fromUtf8("graphicsView"))
        self.layoutWidget = QtGui.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 500, 451, 68))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.splitter_2 = QtGui.QSplitter(self.layoutWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.layoutWidget1 = QtGui.QWidget(self.splitter_2)
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.gridLayout = QtGui.QGridLayout(self.layoutWidget1)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.layoutWidget1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.layoutWidget1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.B_combo = QtGui.QComboBox(self.layoutWidget1)
        self.B_combo.setObjectName(_fromUtf8("B_combo"))
        self.B_combo.addItem(_fromUtf8(""))
        self.B_combo.addItem(_fromUtf8(""))
        self.B_combo.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.B_combo, 1, 2, 1, 1)
        self.R_combo = QtGui.QComboBox(self.layoutWidget1)
        self.R_combo.setObjectName(_fromUtf8("R_combo"))
        self.R_combo.addItem(_fromUtf8(""))
        self.R_combo.addItem(_fromUtf8(""))
        self.R_combo.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.R_combo, 1, 0, 1, 1)
        self.G_combo = QtGui.QComboBox(self.layoutWidget1)
        self.G_combo.setObjectName(_fromUtf8("G_combo"))
        self.G_combo.addItem(_fromUtf8(""))
        self.G_combo.addItem(_fromUtf8(""))
        self.G_combo.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.G_combo, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.layoutWidget1)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 2, 1, 1)
        self.horizontalLayout_2.addWidget(self.splitter_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton = QtGui.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.butt_cancel = QtGui.QPushButton(self.layoutWidget)
        self.butt_cancel.setObjectName(_fromUtf8("butt_cancel"))
        self.verticalLayout.addWidget(self.butt_cancel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.layoutWidget2 = QtGui.QWidget(Form)
        self.layoutWidget2.setGeometry(QtCore.QRect(10, 480, 450, 20))
        self.layoutWidget2.setObjectName(_fromUtf8("layoutWidget2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.check_fixed = QtGui.QCheckBox(self.layoutWidget2)
        self.check_fixed.setObjectName(_fromUtf8("check_fixed"))
        self.horizontalLayout.addWidget(self.check_fixed)
        self.check_autenh = QtGui.QCheckBox(self.layoutWidget2)
        self.check_autenh.setObjectName(_fromUtf8("check_autenh"))
        self.horizontalLayout.addWidget(self.check_autenh)
        self.check_cont = QtGui.QCheckBox(self.layoutWidget2)
        self.check_cont.setObjectName(_fromUtf8("check_cont"))
        self.horizontalLayout.addWidget(self.check_cont)
        self.stretconst = QtGui.QSlider(Form)
        self.stretconst.setGeometry(QtCore.QRect(10, 450, 271, 22))
        self.stretconst.setMaximum(100)
        self.stretconst.setSingleStep(1)
        self.stretconst.setPageStep(1)
        self.stretconst.setOrientation(QtCore.Qt.Horizontal)
        self.stretconst.setTickPosition(QtGui.QSlider.TicksBelow)
        self.stretconst.setTickInterval(10)
        self.stretconst.setValue(50)
        self.stretconst.setObjectName(_fromUtf8("weight_2"))
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(10, 430, 241, 20))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.advButton = QtGui.QPushButton(Form)
        self.advButton.setGeometry(QtCore.QRect(370, 450, 90, 32))
        self.advButton.setObjectName(_fromUtf8("pushButton"))
        self.check_satur = QtGui.QCheckBox(Form)
        self.check_satur.setGeometry(QtCore.QRect(10, 595, 153, 20))
        self.check_satur.setChecked(False)
        self.check_satur.setObjectName(_fromUtf8("check_satur"))
        self.check_inten = QtGui.QCheckBox(Form)
        self.check_inten.setGeometry(QtCore.QRect(190, 595, 151, 20))
        self.check_inten.setChecked(False)
        self.check_inten.setObjectName(_fromUtf8("check_inten"))
        self.huetr_lb = QtGui.QLabel(Form)
        self.huetr_lb.setGeometry(QtCore.QRect(10, 625, 111, 16))
        self.huetr_lb.setObjectName(_fromUtf8("huetr_lb"))
        self.huetr = QtGui.QSlider(Form)
        self.huetr.setGeometry(QtCore.QRect(10, 655, 241, 22))
        self.huetr.setMaximum(100)
        self.huetr.setSingleStep(1)
        self.huetr.setPageStep(1)
        self.huetr.setOrientation(QtCore.Qt.Horizontal)
        self.huetr.setTickPosition(QtGui.QSlider.TicksBelow)
        self.huetr.setTickInterval(10)
        self.huetr.setValue(0)
        self.huetr.setObjectName(_fromUtf8("huetr"))
       
        self.path=path
        self.op1=False
        self.op2=False
        self.op3=False
        self.op4=False
        self.op5=False
        self.huecorrec=0
        self.SC=50
        self.RC=0
        self.GC=1
        self.BC=2
        self.adv=0
        
        self.R_combo.activated.connect(functools.partial(R_comboch, self))
        self.G_combo.activated.connect(functools.partial(G_comboch, self))
        self.B_combo.activated.connect(functools.partial(B_comboch, self))
        self.check_autenh.stateChanged.connect(functools.partial(autenhch, self))
        self.check_fixed.stateChanged.connect(functools.partial(fixedch, self))
        self.check_cont.stateChanged.connect(functools.partial(contch, self))
        self.check_satur.stateChanged.connect(functools.partial(saturch, self))
        self.check_inten.stateChanged.connect(functools.partial(intench, self))
        self.pushButton.clicked.connect(functools.partial(self.applied, Form))
        self.advButton.clicked.connect(functools.partial(self.advanced, Form))
        self.stretconst.valueChanged.connect(functools.partial(stretch, self))
        self.huetr.valueChanged.connect(functools.partial(hue_trch, self))
        #QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.applied(Form))
        QtCore.QObject.connect(self.butt_cancel, QtCore.SIGNAL(_fromUtf8("clicked()")), Form.reject)

        
        self.mode1=ds(self.path,self.op1,self.op2,self.op3,self.op4,self.op5,self.huecorrec,self.SC,self.RC,self.GC,self.BC)
        
        QtImage1 = ImageQt.ImageQt(self.mode1)
        QtImage2 = QtGui.QImage(QtImage1)
        self.pic.setPixmap(QtGui.QPixmap.fromImage(QtImage2))
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "PCA Processing", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "R channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "G channel", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.B_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.R_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(0, QtGui.QApplication.translate("Form", "Comp. 2", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(1, QtGui.QApplication.translate("Form", "Comp. 1", None, QtGui.QApplication.UnicodeUTF8))
        self.G_combo.setItemText(2, QtGui.QApplication.translate("Form", "Comp. 3", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "B channel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Standard Deviation", None, QtGui.QApplication.UnicodeUTF8))
        self.huetr_lb.setText(QtGui.QApplication.translate("Form", "Hue alteration", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Form", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.butt_cancel.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.advButton.setText(QtGui.QApplication.translate("Form", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
        self.check_fixed.setText(QtGui.QApplication.translate("Form", "Fixed offset", None, QtGui.QApplication.UnicodeUTF8))
        self.check_cont.setText(QtGui.QApplication.translate("Form", "Auto-contrast components", None, QtGui.QApplication.UnicodeUTF8))
        self.check_autenh.setText(QtGui.QApplication.translate("Form", "Auto-enhacement", None, QtGui.QApplication.UnicodeUTF8))
        self.check_satur.setText(QtGui.QApplication.translate("Form", "Saturation stretching", None, QtGui.QApplication.UnicodeUTF8))
        self.check_inten.setText(QtGui.QApplication.translate("Form", "Intensity stretching", None, QtGui.QApplication.UnicodeUTF8))

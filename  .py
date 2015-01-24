# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created: Sun Jul  7 16:02:00 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
from formlayout import fedit

def inicio(path):
    datalist=[('Component',[0,'1st','2nd','3rd']),]
    met=fedit(datalist, title="Select Method")
    if met==[0]:
        name='/comp1.tif'
    if met==[1]:
        name='/comp2.tif'
    if met==[2]:
        name='/comp3.tif'
    image=np.array(Image.open(path+'/'+name))
    clahe(image)
    
    datalist=[('Clip Limit',[0,'None','2','4','6','8','10','12']),]
    met=fedit(datalist, title="Select Clip Limit")
    if met==[1]: cl=2.0
    if met==[2]: cl=4.0
    if met==[3]: cl=6.0
    if met==[4]: cl=8.0
    if met==[5]: cl=10.0
    if met==[6]: cl=12.0
    
    image=cv2.createCLAHE(clipLimit=cl, tileGridSize=(4,4)).apply(image.astype(np.uint8))
    plt.close()
    
    maps=[m for m in plt.cm.datad if not m.endswith("_r")]
    maps=[0]+maps
    maps.sort()
    print maps
    
    """colormap(image)
    
    datalist=[('Clip Limit',[0,'Gray','Jet','Hot','Spring','Gnuplot','Terrain']),]
    met=fedit(datalist, title="Select Clip Limit")
    if met==[1]: Image.fromarray(np.uint8(plt.cm.gray(image)*255)).save(path+'temp_col.tif')
    if met==[2]: Image.fromarray(np.uint8(plt.cm.jet(image)*255)).save(path+'temp_col.tif')
    if met==[3]: Image.fromarray(np.uint8(plt.cm.hot(image)*255)).save(path+'temp_col.tif')
    if met==[4]: Image.fromarray(np.uint8(plt.cm.spring(image)*255)).save(path+'temp_col.tif')
    if met==[5]: Image.fromarray(np.uint8(plt.cm.gnuplot(image)*255)).save(path+'temp_col.tif')
    if met==[6]: Image.fromarray(np.uint8(plt.cm.terrain(image)*255)).save(path+'temp_col.tif')"""
    
def clahe(a):    
    clahe1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4)).apply(a.astype(np.uint8))
    clahe2 = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4,4)).apply(a.astype(np.uint8))
    clahe3 = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(4,2)).apply(a.astype(np.uint8))
    clahe4 = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4,4)).apply(a.astype(np.uint8))
    clahe5 = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(4,4)).apply(a.astype(np.uint8))
    clahe6 = cv2.createCLAHE(clipLimit=12.0, tileGridSize=(4,4)).apply(a.astype(np.uint8))
    fig,((ax1,ax2,ax3),(ax4,ax5,ax6))=plt.subplots(nrows=2,ncols=3,figsize=(20,30))
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.imshow(clahe1,cmap='gray')
    ax1.set_title('Clip limit 2.0')
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax2.imshow(clahe2,cmap='gray')
    ax2.set_title('Clip limit 4.0')
    ax3.xaxis.set_visible(False)
    ax3.yaxis.set_visible(False)
    ax3.imshow(clahe3,cmap='gray')
    ax3.set_title('Clip limit 6.0')
    ax4.xaxis.set_visible(False)
    ax4.yaxis.set_visible(False)
    ax4.imshow(clahe4,cmap='gray')
    ax4.set_title('Clip limit 8.0')
    ax5.xaxis.set_visible(False)
    ax5.yaxis.set_visible(False)
    ax5.imshow(clahe5,cmap='gray')
    ax5.set_title('Clip limit 10.0')
    ax6.xaxis.set_visible(False)
    ax6.yaxis.set_visible(False)
    ax6.imshow(clahe6,cmap='gray')
    ax6.set_title('Clip limit 12.0')
    plt.show()

    fig2,((bx1,bx2,bx3),(bx4,bx5,bx6))=plt.subplots(nrows=2,ncols=3,figsize=(20,30))
    bx1.hist(clahe1.flatten(),50,color='gray')
    bx1.set_xlim(0,255)
    bx1.set_title('Clip limit 2.0, histogram')
    bx2.set_xlim(0,255)
    bx2.hist(clahe2.flatten(),50,color='gray')
    bx2.set_title('Clip limit 4.0, histogram')
    bx3.set_xlim(0,255)
    bx3.hist(clahe3.flatten(),50,color='gray')
    bx3.set_title('Clip limit 6.0, histogram')
    bx4.set_xlim(0,255)
    bx4.hist(clahe4.flatten(),50,color='gray')
    bx4.set_title('Clip limit 8.0, histogram')
    bx5.set_xlim(0,255)
    bx5.hist(clahe5.flatten(),50,color='gray')
    bx5.set_title('Clip limit 10.0, histogram')
    bx6.set_xlim(0,255)
    bx6.hist(clahe6.flatten(),50,color='gray')
    bx6.set_title('Clip limit 12.0, histogram')

    plt.show()

def colormap(a):
    fig,((ax1,ax2,ax3),(ax4,ax5,ax6))=plt.subplots(nrows=2,ncols=3,figsize=(20,30))
    ax1.xaxis.set_visible(False)
    ax1.yaxis.set_visible(False)
    ax1.imshow(a,cmap='gray')
    ax1.set_title('Gray')
    ax2.xaxis.set_visible(False)
    ax2.yaxis.set_visible(False)
    ax2.imshow(a,cmap='jet')
    ax2.set_title('Jet')
    ax3.xaxis.set_visible(False)
    ax3.yaxis.set_visible(False)
    ax3.imshow(a,cmap='hot')
    ax3.set_title('Hot')
    ax4.xaxis.set_visible(False)
    ax4.yaxis.set_visible(False)
    ax4.imshow(a,cmap='spring')
    ax4.set_title('Spring')
    ax5.xaxis.set_visible(False)
    ax5.yaxis.set_visible(False)
    ax5.imshow(a,cmap='gnuplot')
    ax5.set_title('Gnuplot')
    ax6.xaxis.set_visible(False)
    ax6.yaxis.set_visible(False)
    ax6.imshow(a,cmap='terrain')
    ax6.set_title('Terrain')
    plt.show()

#!/usr/bin/env python
# -*- coding: utf8 -*-
##es necesario instalar gphoto2 y dcraw
import os,gdal,pylab,math,colorsys,time
from PIL import Image,ImageOps
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Frame
from skimage import color
from numpy import *
from scipy import misc
from scipy import linalg as ln
from scipy.cluster.vq import *
from scipy.misc import imresize

# Captura de imagen en NEF, es necesario que la cámara esté en NEF
def capture_nikon(path):
    run = 'gphoto2 --capture-image-and-download --filename "'+path+'/orignef.nef"'
    os.system(run)

  
def conversion(path,fname):
    filename = gdal.Open(fname)
    br=filename.GetRasterBand(1).ReadAsArray()
    try:
        bg=filename.GetRasterBand(2).ReadAsArray()
    except:
        raise
    bb=filename.GetRasterBand(3).ReadAsArray()

    matrix = array([br,bg,bb],'f')
    return matrix

def histeq(im,nbr_bins=256):
    #get image histogram
    imhist,bins = histogram(im.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum() #cumulative distribution function
    cdf = 255 * cdf / cdf[-1] #normalize

    #use linear interpolation of cdf to find new pixel values
    im2 = interp(im.flatten(),bins[:-1],cdf)

    return im2.reshape(im.shape), cdf
  
def pre_process(path):  #realiza el PCA y lo guarda en una matriz
    fullname=path+'/cmatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
        
    m,n=matrix[0].shape
    
    pcamatrix=array([matrix[0].flatten(),matrix[1].flatten(),matrix[2].flatten()])
    M = cov(pcamatrix)
    MC = corrcoef(pcamatrix)
    e,EV = linalg.eigh(M) # Calculamos los autovectores y los autovalores
    sum = cumsum(e) # Suma de los autovalores para hallar porcentaje
    por =(e*100)/sum[2] #Porcentaje de varianza explicada
    
    f = open(path+"/pcadata.txt", "w")
    f.write("PyDRA PCA Analysis results\n\n")
    f.write("Covariance matrix\n")
    for row in M:
        f.write(str(row[0])+' '+str(row[1])+' '+str(row[2])+'\n')
        
    f.write('\n')
    f.write("Correlation matrix\n")
    for row in MC:
        f.write(str(row[0])+' '+str(row[1])+' '+str(row[2])+'\n')
    f.write('\n')   
    f.write("Eigenvalues\n")
    f.write(str(e[2])+' '+str(e[1])+' '+str(e[0])+'\n')
    f.write('\n')   
    f.write("Explained variance (percentage)\n")
    f.write(str(por[2])+' '+str(por[1])+' '+str(por[0])+'\n')
    f.write('\n')   
    f.write("Eigenvectors\n")
    for row in EV:
        f.write(str(row[0])+' '+str(row[1])+' '+str(row[2])+'\n')
    f.write('\n')   
    f.close()    
    
    tmp = dot(pcamatrix.T,EV).T #this is the compact trick
    tmp2 = tmp[::-1].reshape(3,m,n) #ordenar el producto de la matriz por los autovectores
    matrixsv=path+'/pcamatrix'
    savez(matrixsv,tmp2)

# Procesado de NEF
def process(fname,path):
  
    nef = path+'/orignef.nef'
    copy = 'cp '+fname+' '+nef
    os.system(copy)
    convert ='dcraw -j -W -T -6 '+nef
    os.system(convert)
    archiv = path+'/orignef.tif'
    archiv1 = archiv+'f'
    os.rename(archiv1,archiv)

# Compuesto RGB
def composite(c1,c2,c3,path,name):
    r = Image.open(c1)
    g = Image.open(c2)
    b = Image.open(c3)
    compRGB = path+'/'+name+'.tif'
    Image.merge('RGB',(r,g,b)).save(compRGB)

#Saturacion rojo

def satur(path,fact,op1,svf,sav,rad):
    from skimage import color

    fullname=path+'/cmatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
    
    a1=amax(array([amax(matrix[0]),amax(matrix[1]),amax(matrix[2])]))
        
    if rad==8:
        rgbmatrix=(matrix.T)/255.0
    elif rad==16:
        rgbmatrix=(matrix.T)/a1
    
    h,s,v=(color.rgb2hsv(rgbmatrix)).T

    if os.path.isfile(path+'/pcamatrix.npz') == False: 
        pre_process(path)
    fullname = path +'/pcamatrix.npz'
    tmp=load(fullname)
    tmp2=tmp['arr_0']
    fact=fact*1.0
    if op1==True:
        tmp2[2],_=histeq(tmp2[2])
    splus3 =((tmp2[2]/fact))+(s)
    splus4 = splus3/amax(splus3)

    hsvmatrix=array([h,splus4,v]).T
    r,g,b=(color.hsv2rgb(hsvmatrix)).T
    fin = array([(r*255)/amax(r),(g*255)/amax(g),(b*255.0)/amax(b)])
    
    comp = path+'/Sat.tif'
    mode = misc.toimage(fin)
    mode.save(comp)
    if sav==1:
        matrixsv=path+'/smatrix'
        savez(matrixsv,fin)

# K-means
def k_means(classes,mat,path,svf):
    order=array([4,4,4])
    fullname=path+'/'+mat+'.npz'
    tmp=load(fullname)
    
    prematrix = tmp['arr_0']
    mask=load(path+'/cmatrix.npz')['arr_0']
    try:
        prmatrix[mask==0,0,0]=0,0,0
    
    except:
        pass
    
    try:
        order= tmp['arr_1']
        rc=order[0]
        gc=order[1]
        bc=order[2]
        matrix = array([prematrix[rc].flatten(),prematrix[gc].flatten(),prematrix[bc].flatten()],'f').T
    except:
        matrix = array([prematrix[0].flatten(),prematrix[1].flatten(),prematrix[2].flatten()],'f').T
    
    #Comprobando si hay mas de una matriz igual
    
    if (matrix[:,0]==matrix[:,1]).all() == True and (matrix[:,0]==matrix[:,2]).all() == True:
        matrix = array([prematrix[0].flatten()],'f').T
    elif (matrix[:,0]==matrix[:,1]).all() == True:
        matrix = array([prematrix[0].flatten(),prematrix[2].flatten()],'f').T
    elif (matrix[:,0]==matrix[:,2]).all() == True or (matrix[:,1]==matrix[:,2]).all():
        matrix = array([prematrix[0].flatten(),prematrix[1].flatten()],'f').T
    
    if matrix.shape[1] > 1:
        for i in range (0,matrix.shape[1]): #convirtiendo las matrices en positivas
            if amin(matrix[...,i]) < 1:
                matrix[...,i] = matrix[...,i]+fabs(amin(matrix[...,i]))+1
                #print amin(matrix[...,i])
    
        _,idres=kmeans2(matrix,classes,iter=40)
    else:
        idres,_=histeq(matrix,nbr_bins=classes)
    
    #Ordenar por posibilidad de que pertenezcan a pinturas
    m,n=prematrix[0].shape
    idx=idres.reshape(m,n)
    if os.path.isfile(path+'/pcamatrix.npz') == True:
        fullname = path +'/pcamatrix.npz'
        tmp=load(fullname)
        comp3=(tmp['arr_0'])[2]    
        e=[]
    
        for i in range (0,classes):
            mask = idx==i
            e.append([i,(mean(comp3[mask])*-1)])
        sbm=sorted(e, key=lambda tup: tup[1])
        kk=copy(idx)
        for i in range (0,classes):
            mask = idx==(sbm[i])[0]
            kk[mask]=i
    else:
        kk=idx
    kmeanfile =path+'/kmeans.tif'
    
    mode = misc.toimage(kk)
    mode.save(kmeanfile)
    svf= svf[0:4]+'a'
    return kk,svf
   
# PCA
def pca(X,rad,path,op1,op2,op3,op4,RC,GC,BC,svf,sav):
    if svf[0]=='n' and op4==False and op1 ==False:
        pre_process(path)
        fullname = path +'/pcamatrix.npz'
        tmp=load(fullname)
        tmp2=tmp['arr_0']
        full = path +'/pcamatrix'
        ordermat=array([RC,GC,BC])
        savez(full,tmp2,ordermat)
        svf= 'a'+svf[1:5]
    elif svf[0]=='a' and op4==False and op1 ==False:
        fullname = path +'/pcamatrix.npz'
        tmp=load(fullname)
        tmp2=tmp['arr_0']
        full = path +'/pcamatrix'
        ordermat=array([RC,GC,BC])
        savez(full,tmp2,ordermat)
    else:
        fullname=path+'/cmatrix.npz'
        tmp=load(fullname)
        matrix = tmp['arr_0']
        m,n=matrix[0].shape
        if op4== True:
            immatrix = array([matrix[0].flatten(),matrix[2].flatten(),matrix[1].flatten()],'f')
        else:
            immatrix = array([matrix[0].flatten(),matrix[1].flatten(),matrix[2].flatten()],'f')
        #Pasa la opcion 1, ecualizar automaticamente la imagen
        if op1== True:
            immatrix,_=histeq(immatrix)####AQUI
        M = cov(immatrix)
        e,EV = ln.eigh(M)
        sumtot = cumsum(e)
        por =(e*100)/sumtot[2]
        tmp = dot(immatrix.T,EV).T #this is the compact trick
        tmp2 = tmp[::-1].reshape(3,m,n) #ordenar el producto de la matriz por los autovectores
        matrixsv=path+'/alt_pcamatrix'
        
        #comprobar
        
        
        
        if sav==1:
            matrixsv=path+'/alt_pcamatrix'
            ordermat=array([RC,GC,BC])
            savez(matrixsv,tmp2,ordermat)
            svf= svf[0]+'a'+svf[2:5]
    #Pasa la opcion 2, ecualizar automaticamente la imagen
    if op2== True:
        V,_=histeq(tmp2)
    else:
        V=tmp2

    comp1=path+'/comp1.tif'
    comp2=path+'/comp2.tif'
    comp3=path+'/comp3.tif'
    """if tmp2[2].min()>0: tmp2[2]=tmp2[2]-tmp2[2].min()
    if tmp2[2].min()<0: tmp2[2]=tmp2[2]+(tmp2[2].min()* -1)
    c3=((tmp2[2]*255)/(tmp2[2].max())).astype(uint8)"""
    misc.toimage(V[0],mode='L').save(comp1)
    misc.toimage(V[1],mode='L').save(comp2)
    misc.toimage(V[2],mode='L').save(comp3)

    if RC == 0: RS=comp1
    if RC == 1: RS=comp2
    if RC == 2: RS=comp3
    if GC == 0: GS=comp1
    if GC == 1: GS=comp2
    if GC == 2: GS=comp3
    if BC == 0: BS=comp1
    if BC == 1: BS=comp2
    if BC == 2: BS=comp3
  
    composite(RS,GS,BS,path,'CompRGB')
    return svf


    if op3==True:
        pdfpath = z+'/'+w+'_results.pdf'
        pdfmetrics.registerFont(TTFont('Arial','Arial.ttf'))
        c = canvas.Canvas(pdfpath)
        c.setFont('Arial',16)
        title ='Report for filename '+w
        c.drawString(40,800,title)
        c.setFont('Arial',12)
        if rad == 8:
            typ = 'RGB. Color depth: 8 bits per channel'
        else:
            typ = 'RGB. Color depth: 16 bits per channel'
        c.drawString(40,760,typ)
        size ='Pixel size: '+str(m)+' x '+str(n)
        c.drawString(40,740,size)

        c.drawString(40,690,'Covariance matrix')
        y = 670
        x = 40
        for i in range (0,3):
            for j in range (0,3):
                c.drawString(x,y,str(around(M[i,j],decimals=5)))
                x=x+100
            x=40
            y=y-20
        c.drawString(40,590,'Correlation coefficients')
        y = 570
        x = 40
        for i in range (0,3):
            for j in range (0,3):
                c.drawString(x,y,str(around(MC[i,j],decimals=5)))
                x=x+100
            x=40
            y=y-20
        c.drawString(40,490,'Eigenvalues')
        eord = sort(e)[::-1]
        x = 40
        for j in range (0,3):
            c.drawString(x,470,str(around(eord[j],decimals=5)))
            x=x+100
        c.drawString(40,440,'Percentage of explained variance')
        pord = sort(por)[::-1]
        x = 40
        for j in range (0,3):
            c.drawString(x,420,str(around(pord[j],decimals=5)))
            x=x+100
        c.drawString(40,390,'Eigenvectors, UNORDERED')
        y = 370
        x = 40
        for i in range (0,3):
            for j in range (0,3):
                c.drawString(x,y,str(around(EV[i,j],decimals=5)))
                x=x+100
            x=40
            y=y-20
        c.showPage()
        c.save()
  
def stretch(X,path,op1,op2,op3,op4,op5,huecorrec,SC,RC,GC,BC,sav):

    fullname=path+'/cmatrix.npz'
    tmp=load(fullname)
    matrix = tmp['arr_0']
    
    #Pasa la opcion 1, ecualizar automaticamente la imagen
    if op1== True:
        tempmatrix,_=histeq(matrix)
    else:
        tempmatrix=matrix
    
    _,m,n=tempmatrix.shape
    
    a_medias = zeros(tempmatrix.shape)
    for i in range (0,3):
            a_medias[i]=(tempmatrix[i]-mean(tempmatrix[i]))/std(tempmatrix[i])

    immatrix=array([a_medias[0].flatten(),a_medias[1].flatten(),a_medias[2].flatten()])
    
    M = cov(immatrix)
    e,EV = ln.eigh(M)
    tmp = dot(immatrix.T,EV).T
    
    c=array([tmp[0].reshape(m,n).T,tmp[1].reshape(m,n).T,tmp[2].reshape(m,n).T]).T
    
    s_matrix=zeros((3,3),'f')
    for i in range (0,3):
            s_matrix[i,i]=1/sqrt(e[i])
    
    d=dot(c,s_matrix)
    e=dot(d,EV.T)
    f=zeros((3,3))
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
    
    str4=zeros((3,m,n))
    
    str4[0] = h[:,:,RC]
    str4[1] = h[:,:,GC]
    str4[2] = h[:,:,BC]
    
    
    if op4 == True or op5==True or huecorrec >0: 
        
        str4=str4.T
        
        print(str4.shape)
    
        hue,s,v=(color.rgb2hsv(str4/255.0)).T
        if op4 ==True:
            print('paso 4')
            sst=(s-s.min())/s.max()
        else:
            sst=s
    
        if op5 ==True:
            vst=(v-v.min())/v.max()
        else:
            vst=v
    
        if huecorrec > 0:
            hue = hue + (huecorrec/100.0)
            mask = (hue>1)
            hue[mask]=hue[mask]-(huecorrec/100.0)
        else:
            hue=hue
             
        hsvmatrix=array([hue,sst,vst]).T
        r,g,b=(color.hsv2rgb(hsvmatrix)).T
        str4=array([r,g,b])
    
    comp1=path+'/dstr.tif'
    
    
    if sav==1:
        matrixsv=path+'/dsmatrix'
        
        savez(matrixsv,str4)

    #Pasa la opcion 2, ecualizar automaticamente la imagen
    if op2== True:
        mode1 = ImageOps.equalize(misc.toimage(str4)).save(comp1)
    else:
        mode1 = misc.toimage(str4).save(comp1)

def color_class(num,datalist,a):
    from formlayout import fedit

    col1,col2,col3,col4,col5,col6,col7=fedit(datalist,title="Assign colors")
    if a==1:
        num=zeros((7,3),int)
    
    col1 = col1.lstrip('#')
    num[0,0],num[0,1],num[0,2]=tuple(int(col1[i:i+2], 16) for i in range(0, 6, 2))
    
    col2 = col2.lstrip('#')
    num[1,0],num[1,1],num[1,2]=tuple(int(col2[i:i+2], 16) for i in range(0, 6, 2))
    
    col3 = col3.lstrip('#')
    num[2,0],num[2,1],num[2,2]=tuple(int(col3[i:i+2], 16) for i in range(0, 6, 2))
    
    col4 = col4.lstrip('#')
    num[3,0],num[3,1],num[3,2]=tuple(int(col4[i:i+2], 16) for i in range(0, 6, 2))
    
    col5 = col5.lstrip('#')
    num[4,0],num[4,1],num[4,2]=tuple(int(col5[i:i+2], 16) for i in range(0, 6, 2))
    
    col6 = col6.lstrip('#')
    num[5,0],num[5,1],num[5,2]=tuple(int(col6[i:i+2], 16) for i in range(0, 6, 2))
    
    col7 = col7.lstrip('#')
    num[6,0],num[6,1],num[6,2]=tuple(int(col7[i:i+2], 16) for i in range(0, 6, 2))
    return num
    


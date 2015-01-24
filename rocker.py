import numpy as np
import cv2
import sys,os
from scipy.ndimage import zoom
from PIL import Image
from formlayout import fedit

def onmouse(event,x,y,flags,param):
    global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over

    if event == cv2.EVENT_MOUSEMOVE:
        if drawing==1:
            cv2.circle(img,(x,y),thickness,value['color'],-1)
        """cv2.circle(mask,(x,y),thickness,value['val'],-1)"""
    if event == cv2.EVENT_RBUTTONDOWN:
        cv2.circle(img,(x,y),thickness,value['color'],-1)

classarry=np.load('nclass.npy')
l=[]
l.append(0)
for a in classarry:
    l.append(a)

datalist=[('Layer to edit',l),]

met=fedit(datalist, title="Select Class to edit")
numb_class=int(met[0])
        
BLACK = [255,255,255]         # sure BG
DRAW_BG = {'color' : BLACK, 'val' : 255}
drawing=0
thickness = 10          # brush thickness

if len(sys.argv) == 2:
    try:
        with open(sys.argv[1]+'/kmeans_edited.tif'):
            filename = sys.argv[1]+'/kmeans_edited.tif'
    except:
        filename = sys.argv[1]+'/kmeans.tif'

img2=np.array(Image.open(filename))
img2=np.dstack([img2[:,:,2],img2[:,:,1],img2[:,:,0]])
img = img2*1
img[img>254]=254

scale=0
while (img.shape[1] > 900):
    scale=scale+2
    img=cv2.resize(img,(int(img.shape[1]/scale), int(img.shape[0]/scale)), interpolation=cv2. INTER_AREA)
    
cv2.namedWindow('input',cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('input',onmouse)

while(1):

        cv2.imshow('input',img)
        k = 0xFF & cv2.waitKey(1)

    # key bindings
        if k == 27:         # esc to exit
            break
        elif k == ord('0'): # BG drawing
            value = DRAW_BG
            drawing=1
        elif k == ord('1'):
            drawing=0
        elif k == ord('5'):
            thickness=thickness+2
        elif k == ord('6'):
            thickness=thickness-2

        elif k == ord('s'): # save image
            print scale
            img[img<255]=0
            if scale==4:
                scale=8
            mask=zoom(img[:,:,0], scale, order=0)
            wall=np.zeros((img2[:,:,0].shape))
            wall[:mask.shape[0],:mask.shape[1]]=mask
            
            try:
                with open(sys.argv[1]+'/kmatrix_edited.npz'):
                    matrixname = sys.argv[1]+'/kmatrix_edited.npz'
            except:
                matrixname = sys.argv[1]+'/kmatrix.npz'          
            
            
            m=np.load(matrixname)['arr_0']
            kmatrix=np.load(matrixname)['arr_2']
            classes=np.load(matrixname)['arr_1']
            

            r1=np.zeros((kmatrix.shape)).astype(np.uint8)
            g1=np.zeros((kmatrix.shape)).astype(np.uint8)
            b1=np.zeros((kmatrix.shape)).astype(np.uint8)
        
            r1=r1+255
            g1=g1+255
            b1=b1+255

            count=0
            for a in classes:
                if a==0:
                    ref=count
                count=count +1
            
            for i in xrange(0,len(np.unique(kmatrix))):
                z=classes[i]
                r1[kmatrix==i]=m[z,0]
                g1[kmatrix==i]=m[z,1]
                b1[kmatrix==i]=m[z,2]
                if z==numb_class:
                    r1[(kmatrix==i)&(wall==255)]=m[0,0]
                    g1[(kmatrix==i)&(wall==255)]=m[0,1]
                    b1[(kmatrix==i)&(wall==255)]=m[0,2]
                    kmatrix[(kmatrix==i)&(wall==255)]=ref
            np.savez(sys.argv[1]+'/kmatrix_edited.npz',m,classes,kmatrix)
            
            r1[0,0]=0
            g1[0,0]=0
            b1[0,0]=0
            r1[1,1]=255
            g1[1,1]=255
            b1[1,1]=255
            
            a=np.dstack([r1,g1,b1])
             
            Image.fromarray(a).save(sys.argv[1]+'/kmeans_edited.tif')
            Image.fromarray(a).save('/Users/enrique/Downloads/kmeans_edited.tif')
            
            """img2=np.dstack([img2[:,:,2],img2[:,:,1],img2[:,:,0]])
            Image.fromarray(img2.astype(np.uint8)).save(sys.argv[1]+'/kmeans_edited.tif')"""
            

            
            #Image.fromarray(wall.astype(np.uint8)).save('/Users/enrique/Downloads/klop1.jpg')

        
            
            break
cv2.destroyAllWindows()
os.system('rm .masking')
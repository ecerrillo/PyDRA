import numpy as np
import cv2
import sys,os
from scipy.ndimage import zoom
from PIL import Image

def onmouse(event,x,y,flags,param):
    global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over

    if event == cv2.EVENT_MOUSEMOVE:
        if drawing==1:
            cv2.circle(img,(x,y),thickness,value['color'],-1)
        """cv2.circle(mask,(x,y),thickness,value['val'],-1)"""
    if event == cv2.EVENT_RBUTTONDOWN:
        cv2.circle(img,(x,y),thickness,value['color'],-1)


BLACK = [0,0,0]         # sure BG
DRAW_BG = {'color' : BLACK, 'val' : 0}
drawing=0
thickness = 10          # brush thickness

if len(sys.argv) == 2:
    filename = sys.argv[1]+'/cmatrix.npz' # for drawing purposes

img3=(np.load(filename)['arr_0'].T)
img2=np.dstack([img3[:,:,2].T,img3[:,:,1].T,img3[:,:,0].T]).astype(np.uint8)

img = img2*1

img[img==0]=1
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
            img[img>0]=255
            if scale==4:
                scale=8
            mask=zoom(img[:,:,0], scale, order=0)
            print scale
            wall=np.zeros((img2[:,:,0].shape))
            wall[:mask.shape[0],:mask.shape[1]]=mask
            wall=wall.T

            img3[wall==0]=0
            
            img4=np.dstack([img3[:,:,0].T,img3[:,:,1].T,img3[:,:,2].T])
            
            print img3.shape,img4.shape
            Image.fromarray(img4.astype(np.uint8)).save(sys.argv[1]+'/masked.tif')
            
            img3=img3.T
            np.savez(filename,img3)

            
            #Image.fromarray(wall.astype(np.uint8)).save('/Users/enrique/Downloads/klop1.jpg')

        
            
            break
cv2.destroyAllWindows()
os.system('rm .masking')
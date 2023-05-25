import numpy as np
import cv2
import os, stat
import shutil
# if __name__ == '__main__':
def func(crd, name):
    print("CHEGOU NO CROP")
    print(name)
    img = cv2.imread(f"./imagens/{name}")
    mask = np.zeros(img.shape[0:2], dtype=np.uint8)
    print(crd)
    arr = eval("[" + crd + "]")
    points = np.array([arr])
    #method 1 smooth region
    print('aaaaa')
    print(points)
    cv2.drawContours(mask, [points], -1, (255, 255, 255), -1, cv2.LINE_AA)
    #method 2 not so smooth region
    # cv2.fillPoly(mask, points, (255))
    res = cv2.bitwise_and(img,img,mask = mask)
    rect = cv2.boundingRect(points) # returns (x,y,w,h) of the rect
    cropped = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
    ## crate the white background of the same size of original image
    wbg = np.ones_like(img, np.uint8)*255
    cv2.bitwise_not(wbg,wbg, mask=mask)
    # overlap the resulted cropped image on the white background
    dst = wbg+res
    
    # cv2.imwrite("C:/Users/pedro/OneDrive/Ambiente de Trabalho/A.jpg", dst)
    # cv2.imwrite("C:/Users/pedro/OneDrive/Ambiente de Trabalho/original_image.jpg", dst)

    # return "C:/Users/pedro/OneDrive/Ambiente de Trabalho/A.jpg"
    
    cv2.imwrite("A.jpg", dst)
    cv2.imwrite("./static/original_image.jpg", dst)
    return "A.jpg"

    # cv2.imshow("Samed Size White Image", dst)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
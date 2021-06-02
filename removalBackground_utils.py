import cv2 as cv
import numpy as np
import os
import glob
from PIL import Image

def rangeGreen(image, low = [0,80,0], high = [100, 255,255]):
    img_blur = cv.GaussianBlur(image, (5,5), 2)
    hsv_img = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
    hsv_img_copy = hsv_img.copy()
    green_low = np.array(low)
    green_high = np.array(high)
    curr_mask = cv.inRange(hsv_img, green_low, green_high)
    hsv_img[curr_mask > 0] = ([0,0,0])
    hsv_img_copy[curr_mask >0] = ([75,255,200])
    

    # BGR_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)
    return hsv_img, hsv_img_copy

def remove_background(image, raw, threshold=125):
    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # print(threshold)
    thresholdImg = cv.threshold(img_gray, threshold, 255, cv.THRESH_BINARY_INV)[1]

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    morphed = cv.morphologyEx(thresholdImg, cv.MORPH_OPEN, kernel)
    morphed = cv.morphologyEx(morphed, cv.MORPH_CLOSE, kernel)
    
    # Infill image 
    im_floodfill = morphed.copy()
    h , w = morphed.shape[:2]
    mask_floodfill = np.zeros((h + 2, w +2 ), np.uint8)

    cv.floodFill(im_floodfill, mask_floodfill, (0,0), 255)
    im_floodfill_inv = cv.bitwise_not(im_floodfill)
    morphed = morphed | im_floodfill_inv


    cnts = cv.findContours(morphed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
    cnt = sorted(cnts, key= cv.contourArea)[-1]
    mask = cv.drawContours(thresholdImg, cnt, 0, (0,255,0), 0)
    masked = cv.bitwise_and(raw, raw, mask= mask)

    x, y, w, h = cv.boundingRect(cnt)
    destination = masked[y : y + h, x: x + w]
    dst_gray = cv.cvtColor(destination, cv.COLOR_BGR2GRAY)
    _, alpha = cv.threshold(dst_gray, 0, 255, cv.THRESH_BINARY)
    b, g, r = cv.split(destination)

    rgba = [r, g, b, alpha]
    destination = cv.merge(rgba, 4)
    return destination

def create_blank_image(height, width, rgb_color=(0, 0, 255)):
    """
    Creates np.array, each channel of which is filled with value from rgb_color
    
    Was stolen from:
    :source: https://stackoverflow.com/questions/4337902/how-to-fill-opencv-image-with-one-solid-color
    """
    
    image = np.zeros((height, width, 3), np.uint8)
    color = tuple(reversed(rgb_color))
    
    image[:] = color
    
    return image

def crop(image, background_color=(255,255,255)):
    height, width, channel = image.shape
    lenght = width if width>height else height
    coordinate = (0, int(lenght/2 - height/2)) if width>height else (int(lenght/2 - width/2), 0)
    background = create_blank_image(lenght, lenght, background_color)

    background = Image.fromarray(background)
    image = Image.fromarray(image)

    background.paste(image, coordinate, image)
    background = np.array(background)
    return background


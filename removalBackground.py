import cv2 as cv
import numpy as np
import os
import glob
from PIL import Image

# def remove_background(image, threshold):
#     gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
#     threshed = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY_INV)[1]

#     kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
#     morphed = cv.morphologyEx(threshed, cv.MORPH_OPEN, kernel)
#     morphed = cv.morphologyEx(morphed, cv.MORPH_CLOSE, kernel)
    
#     cnts = cv.findContours(morphed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
#     cnt = sorted(cnts, key=cv.contourArea)[-1]
#     mask = cv.drawContours(threshed, cnt, 0, (0, 255, 0), 0)
#     masked_data = cv.bitwise_and(img, img, mask=mask)

#     x, y, w, h = cv.boundingRect(cnt)
#     dst = masked_data[y: y + h, x: x + w]

#     dst_gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
#     _, alpha = cv.threshold(dst_gray, 0, 255, cv.THRESH_BINARY)
#     b, g, r = cv.split(dst)

#     rgba = [r, g, b, alpha]
#     dst = cv.merge(rgba, 4)

#     return dst

# path_current = os.getcwd()
# path_folder = os.path.join(path_current, 'data')
# leaf_list = os.listdir(path_folder)

def get_random(leaf_list, path):
    image_names = os.listdir(path)

    image_name = np.random.choice(image_names, size=1)[0]

    image_path = os.path.join(path, image_name)
    image = cv.imread(image_path)
    return image

    
# # for leaf_class in leaf_list:
# #     print(leaf_class)
# #     path_folder_name = os.path.join(path_folder, leaf_class)
# #     img = get_random(leaf_list, path_folder_name)
# #     # des = remove_background(img, 200.)

# #     cv.imshow(leaf_class, des)
# #     if cv.waitKey(0) & 0xFF == ord('a'):
# #         continue
# # cv.destroyAllWindows()

# path_folder_name = os.path.join(path_folder, leaf_list[2])
# img = get_random(leaf_list, path_folder_name)
# img_blur = cv.GaussianBlur(img, (5,5), 2)
# hsv_img = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
# cv.imshow("HSV", hsv_img)

# green_low = np.array([0 , 80, 0] )
# green_high = np.array([100, 255, 255])
# curr_mask = cv.inRange(hsv_img, green_low, green_high)
# hsv_img[curr_mask > 0] = ([0,0,0])#([75,255,200])
# cv.imshow("Mask", hsv_img)

# RGB_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)
# gray = cv.cvtColor(RGB_img, cv.COLOR_BGR2GRAY)
# cv.imshow("BGR agian", gray)

# det = remove_background(RGB_img, 125.)
# # threshold = cv.threshold(gray, 125, 255, cv.THRESH_BINARY_INV)[1]
# cv.imshow("Remove", det)
# cv.waitKey(0)
# cv.destroyAllWindows()


def rangeGreen(image, low = [0,80,0], high = [100, 255,255]):
    img_blur = cv.GaussianBlur(image, (5,5), 2)
    hsv_img = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
    
    green_low = np.array(low)
    green_high = np.array(high)
    curr_mask = cv.inRange(hsv_img, green_low, green_high)
    hsv_img[curr_mask > 0] = ([0,0,0])

    BGR_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)
    return BGR_img

def remove_background(image, raw, threshold=125):
    img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    threshold = cv.threshold(img_gray, threshold, 255, cv.THRESH_BINARY_INV+ cv.THRESH_OTSU)[1]

    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    morphed = cv.morphologyEx(threshold, cv.MORPH_OPEN, kernel)
    morphed = cv.morphologyEx(morphed, cv.MORPH_CLOSE, kernel)

    cnts = cv.findContours(morphed, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
    cnt = sorted(cnts, key= cv.contourArea)[-1]
    mask = cv.drawContours(threshold, cnt, 0, (0,255,0), 0)
    cv.imshow('Mask', mask)
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

def main():
    green_low = [0, 80, 0]
    green_high = [100, 255, 255]
    path_current = os.getcwd()
    path = os.path.join(path_current, 'data')
    folder_list = os.listdir(path)
    if not os.path.exists(os.path.join(path_current, 'save')):
        os.mkdir(os.path.join(path_current, 'save'))

    for folder_name in folder_list:
        count = 0
        path_folder = os.path.join(path, folder_name)
        path_save = os.path.join(path_current, 'save', folder_name)
        if not os.path.exists(path_save):
            os.mkdir(path_save)
        for path_image in glob.glob(path_folder + "/*.jpg"):
            image = cv.imread(path_image)
            BGR_img = rangeGreen(image, low=green_low, high=green_high)
            dest = remove_background(BGR_img, image)
            final = crop(dest)
            final = cv.resize(final, (608,608))
            path_save_image = os.path.join(path_save, os.path.basename(path_image))
            cv.imwrite(path_save_image, final)
            count +=1
        print(folder_name, "num: ", count)

if __name__ == "__main__":
    # main()
    path_current = os.getcwd()
    path_folder = os.path.join(path_current, 'data')
    leaf_list = os.listdir(path_folder)
    path_folder_name = os.path.join(path_folder, leaf_list[4])
    img = get_random(leaf_list, path_folder_name)
    cv.imshow("Origin", img)
    img_blur = cv.GaussianBlur(img, (5,5), 2)
    hsv_img = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)
    hsv_img1 = hsv_img.copy()
    cv.imshow("HSV", hsv_img)

    green_low = np.array([0 , 80, 0] )
    green_high = np.array([100, 255, 255])
    curr_mask = cv.inRange(hsv_img, green_low, green_high)
    hsv_img[curr_mask > 0] = ([0,100,100])#([75,255,200])
    hsv_img1[curr_mask > 0] = ([0,100,100])
    cv.imshow("Mask", hsv_img1)

    RGB_img = cv.cvtColor(hsv_img, cv.COLOR_HSV2BGR)
    gray = cv.cvtColor(RGB_img, cv.COLOR_BGR2GRAY)
    cv.imshow("BGR agian", gray)

    det = remove_background(RGB_img, img)
    # threshold = cv.threshold(gray, 125, 255, cv.THRESH_BINARY_INV)[1]
    cv.imshow("Remove", det)

    final = crop(det)
    final = cv.resize(final, (608,608))
    cv.imshow("Crop", final)
    cv.waitKey(0)
    cv.destroyAllWindows()












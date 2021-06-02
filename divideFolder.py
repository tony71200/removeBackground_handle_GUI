import os
import glob
import argparse
import numpy as np
import random

def parser():
    args = argparse.ArgumentParser()
    args.add_argument("-i", "--inputPath", type=str, help="Path the folder directory (Full)")
    return args.parse_args()

def moveFile(name_list, new_name_folder):
    if not name_list:
        print("cannot move to ", new_name_folder)
        return
    if not os.path.exists(new_name_folder):
        os.makedirs(new_name_folder)
    for file_name in name_list:
        os.rename(file_name, os.path.join(new_name_folder, file_name))  

def main():
    args =parser()
    if args.inputPath == None:
        print("Khong co dau vao")
        return
    path = args.inputPath
    for folder_name in os.listdir(path):
        path_current = os.path.join(path, folder_name)
        os.chdir(path_current)
        name_list = os.listdir(path_current)
        # name_list = set(name_list)
        np.random.shuffle(name_list)
        # print(type(name_list))
        if (len(name_list) > 500):
            train = name_list[:400]
            val = name_list[400:500]
            test = name_list[500:]
        else:
            train = name_list[:320]
            val = name_list[320:400]
            test = name_list[400:]
        print(folder_name, " :" , len(name_list))
        print("train: {}, val: {}, test: {}".format(len(train), len(val), len(test)))
        moveFile(train, "train")
        moveFile(val, "valid")
        moveFile(test, "test")
        
main()
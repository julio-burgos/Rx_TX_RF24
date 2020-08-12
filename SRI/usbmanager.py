#!/usr/bin/env python
import os
import subprocess
import sys
import time


def read_file_usb(filenamein=None):
    usbpath = "/media/pi/"
    usb = os.listdir(os.path.dirname(usbpath))[0]
    files = os.listdir(os.path.join(usbpath, usb))
    try:
        if filenamein and files.index(filenamein) >= 0:
            filename = files[files.index(filenamein)]
        else:
            filename = files[0]
    except ValueError:
        filename = files[0]
    file = open(os.path.join(usbpath, usb, filename), "rb")
    data = file.read()
    file.close()
    return data


def copy_file(data, filepathtosave):
    file = open(filepathtosave, "wb")
    file.write(data)
    file.close()


def read_copy(fileinput,filepathtosave):
    data = read_file_usb(fileinput)
    copy_file(data, filepathtosave)


def wait_til_usb_connected():
    usbpath = "/media/pi/"
    isconnected= False
    while not isconnected:
        if len(os.listdir(os.path.dirname(usbpath))) != 0 :
            usb = os.listdir(os.path.dirname(usbpath))[0]
            files = os.listdir(os.path.join(usbpath, usb))
            if  len (files)!=0:
                isconnected=True
        time.sleep(0.1)


def is_usb_connected():
    return len(os.listdir(os.path.dirname("/media/pi/"))) == 0


def write_file_usb(fileinput, fileoutput):

    file = open(fileinput, "rb")
    data = file.read()
    file.close()

    usbpath = "/media/pi/"
    usb = os.listdir(os.path.dirname(usbpath))[0]
    copy_file(data, os.path.join(usbpath, usb, fileoutput))
    
def write_data_usb(data, fileoutput):

    usbpath = "/media/pi/"
    usb = os.listdir(os.path.dirname(usbpath))[0]
    copy_file(data, os.path.join(usbpath, usb, fileoutput))

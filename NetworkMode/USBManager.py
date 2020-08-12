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
        # If we find the file specified en filenamein within the USB,
        # we upload such file
        if filenamein and files.index(filenamein) >= 0:
            filename = files[files.index(filenamein)]
        # If we have not introduced an specific name of the file, we
        # upload the first file found in the USB
        else:
            filename = files[0]
    except ValueError:
        # If the filename introduced is not found in the USB, we upload
        # the first file found in the USB
        filename = files[0]
    file = open(os.path.join(usbpath, usb, filename), "rb")
    data = file.read()
    file.close()
    return data


def copy_file(data, filepathtosave):
    file = open(filepathtosave, "wb")
    file.write(data)
    file.close()


def read_copy(fileinput, filepathtosave):
    data = read_file_usb(fileinput)
    copy_file(data, filepathtosave)


def wait_til_usb_connected():
    usbpath = "/media/pi/"
    isconnected = False
    while not isconnected:
        # If we detect a USB, we wil try to look inside its content
        if len(os.listdir(os.path.dirname(usbpath))) != 0:
            usb = os.listdir(os.path.dirname(usbpath))[0]
            files = os.listdir(os.path.join(usbpath, usb))
            # Only if we can access to the actual content of the USB,
            # we will indicate that we have a USB connected
            if len(files) != 0:
                isconnected = True
        time.sleep(0.1)


def is_usb_connected_NM():
    usbpath = "/media/pi/"
    isconnected = False
    time_first = time.time()
    while not isconnected:
        # If we detect a USB, we wil try to look inside its content
        if len(os.listdir(os.path.dirname(usbpath))) != 0:
            usb = os.listdir(os.path.dirname(usbpath))[0]
            files = os.listdir(os.path.join(usbpath, usb))
            # Only if we can access to the actual content of the USB,
            # we will indicate that we have a USB connected
            if len(files) != 0:
                isconnected = True
        time.sleep(0.1)
        time_actual = time.time()
        if time_actual >= time_first + 60:
            break
    return isconnected


def is_usb_connected():
    usbpath = "/media/pi/"
    isconnected = False
    time.sleep(5)
    # If we detect a USB, we wil try to look inside its content
    if len(os.listdir(os.path.dirname(usbpath))) != 0:
        usb = os.listdir(os.path.dirname(usbpath))[0]
        time.sleep(5)
        files = os.listdir(os.path.join(usbpath, usb))
        # Only if we can access to the actual content of the USB,
        # we will indicate that we have a USB connected
        if len(files) != 0:
            isconnected = True
    return isconnected


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

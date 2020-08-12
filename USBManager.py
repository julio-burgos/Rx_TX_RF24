#!/usr/bin/env python
import os
import subprocess
import sys
import time
def read_file_usb():
  usbpath = "/media/pi/"
  usb = os.listdir(os.path.dirname(usbpath))[0]

  filename = os.listdir(os.path.join(usbpath,usb))[0]
  file = open(os.path.join(usbpath,usb,filename), "rb")
  data = file.read()
  file.close()
  return data


def copyfile(data,filepathtosave):
  file = open(filepathtosave,"wb")
  file.write(data)
  file.close()

def copyandread(filepathtosave):
  data = read_file_usb()
  copyfile(data,filepathtosave)

def waittilusbconnected():
  while len(os.listdir(os.path.dirname( "/media/pi/")))==0:
    time.sleep(0.1)
  return read_file_usb()

def isubconnected():
  return len(os.listdir(os.path.dirname( "/media/pi/")))!=0




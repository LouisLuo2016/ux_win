#!/usr/bin/env python
import os
import sys
import time

import loghelper
import qalaunchtime
from adb import adb
from argparse import ArgumentParser

last_start = 0
last_end = 0

def getFwWakeupTime(logoutput):
    startpoint = 0
    endpoint = 0
    fd = open(logoutput, "r")
    logs = fd.readlines()
    for log in logs:
        logElement = loghelper.parse2Element(log, "logcat")
        if "Waking up from sleep" in logElement.tagContent:
            startpoint = logElement.ts
        if "setPowerMode()" in logElement.tagContent or "Failed to set screen crtc_id 6" in logElement.tagContent:
            endpoint = logElement.ts
    fd.close()
    fwWakeupTime = endpoint - startpoint
    return fwWakeupTime

def getKernelWakeupTime(dmesgoutput):
    global last_start, last_end
    startpoint = 0
    endpoint = 0
    fd = open(dmesgoutput, "r")
    dmesglog = fd.readlines()
    for log in dmesglog:
        logElement = loghelper.parse2Element(log, "dmesg")
        if "Enabling non-boot CPUs" in logElement.content:
            startpoint = logElement.ts
        if "Restarting tasks" in logElement.content:
            endpoint = logElement.ts
    fd.close()
    if startpoint == last_start or endpoint == last_end:
        return 0
    else:
        last_start = startpoint
        last_end = endpoint
    kernelWakeupTime = endpoint - startpoint
    return kernelWakeupTime

def doDisplayturnon():
    # get params
    p = ArgumentParser(usage='xxx_on.py -t n -r n', description='Author louis')
    p.add_argument('-r', default=5,  dest='repeat', type=int, help='repeat')
    p.add_argument('-s', action='store_true', dest='skip')
    a = p.parse_known_args(sys.argv)
    repeat = a[0].repeat
    skip = a[0].skip
    caseName = "Display_turn_on"

    # parse exist log file
    if len(sys.argv) == 3:
        kernelWakeupTime = getKernelWakeupTime(sys.argv[1])
        fwWakeupTime = getFwWakeupTime(sys.argv[2])
        print "%d + %d = %d" % (kernelWakeupTime, fwWakeupTime, fwWakeupTime + kernelWakeupTime)
        return

    if skip:
        adb.cmd("shell input keyevent 26").communicate()
        qalaunchtime.clear_logcat()
        
    # create work path
    pwd = os.getcwd()
    os.makedirs(caseName)
    os.chdir(caseName)

    index = 0
    resList = []
    content = caseName
    print content
    logoutput = "log"
    dmesgoutput = "dmesg"
    fwWakeupTime = 0
     
    # loop parse
    adb.cmd("shell settings put system screen_off_timeout 15000").communicate()
    time.sleep(30)
    while index < repeat:      
        qalaunchtime.clear_logcat()
        adb.cmd("shell input keyevent 26").communicate()
        logoutput = "%s_%d.log" % (caseName, index)
        #dmesgoutput = "%s_%d.dmesg" % (caseName, index)
        time.sleep(5)
        qalaunchtime.dump_logcat(logoutput)
        # usb not disconnect, so kernel not used
        #qalaunchtime.dump_dmesg(dmesgoutput)

        fwWakeupTime = getFwWakeupTime(logoutput)
        content = "index %d: %d ms" % (index, fwWakeupTime)
        print content
        index += 1

        resList.append(fwWakeupTime)
        time.sleep(20)
    # prevent subprocess blocked
    adb.raw_cmd("kill-server").communicate()
    qalaunchtime.handleResult(caseName, resList, pwd)   
 
# ----------------------------------------------------------------------------------------------------
doDisplayturnon()

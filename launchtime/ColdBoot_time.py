#!/usr/bin/env python
import os
import re
import time
import sys
import qalaunchtime
from adb import adb
from argparse import ArgumentParser


def getLogs(logname):
    if os.name != "nt":
        bootProgressCommand = "logcat -b all -v time -d | grep -E 'boot_progress'"
    else:
        bootProgressCommand = "logcat -b all -v time -d | findstr boot_progress"

    with open(logname + ".logcat", "w") as f:
        f.write(adb.cmd(bootProgressCommand).communicate()[0])
    with open(logname + ".dmesg", "w") as f:
        f.write(adb.cmd("shell dmesg").communicate()[0])

def parseLogs(logname):
    # parse dmesg
    # kernel launch time
    # dmesgkeyString is used from linux/scripts/bootgraph.pl, it can be used as the timenode for kernel startup end  and init start
    # dmesgKeyString = "Write protecting the"
    dmesg_log = open(logname + ".dmesg", "r")
    dmesgKeyString = "Freeing unused kernel memory"
    line = dmesg_log.readline()
    kernelTime = 0
    while line:
        line = line.strip()
        find = line.find(dmesgKeyString)
        if find != -1:
            # <6>[    4.123123] Freeing unused kernel memory: 852K (ffffffff820c9000 - ffffffff8219e000)
            tempTimeNode = line[line.find("[") :line.find("]")].split(" ")[-1]
            kernelTime = int(float(tempTimeNode)*1000)
            break
        line = dmesg_log.readline()
    dmesg_log.close()

    # parse boot_progress
    # android time
    boot_progress = open(logname + ".logcat", "r")
    logs = boot_progress.readlines()
    bootTs = 0
    for i in xrange(len(logs)):
        log = logs[i]
        g = re.match(r'.*\d{2}:(?P<minute>\d{2}):(?P<sec>\d{2})\.(?P<msec>\d{3}).*I\/(?P<content>.*)', log)
        if g is not None and 'enable_screen' in log:
            g = re.match(r'(?P<key>boot_progress_\w+)\(.*:\s+(?P<duration>\d+).*', g.group('content'))
            bootTs = int(g.group('duration'))
    boot_progress.close()
    return kernelTime + bootTs

'''
    produces for cold boot time info analysis:
    getLogs: dmesg and boot events
    parse the logs and generate the useful result
    output
'''
def doColdbootTime():
    # get params
    p = ArgumentParser(usage='xxx_time.py -t n -r n', description='Author louis')
    p.add_argument('-r', default=5,  dest='repeat', type=int, help='repeat')
    p.add_argument('-s', action='store_true', dest='skip')
    a = p.parse_known_args(sys.argv)
    caseName = "ColdBoot_time"
    num_reboot = a[0].repeat
    skip = a[0].skip
    
    if skip:
        adb.cmd("reboot").communicate()
        time.sleep(80)
        adb.raw_cmd("wait-for-device").communicate()

    # create work path
    pwd = os.getcwd()
    os.makedirs(caseName)
    os.chdir(caseName)
    
    resList = []
    index = 0
    content = caseName
    print content
    launchtime = 0
    logname = "log"

    while (index < num_reboot):
        adb.cmd("reboot").communicate()
        time.sleep(80)
        adb.raw_cmd("wait-for-device").communicate()
        logname = "%s_%d" % (caseName, index)
        getLogs(logname)
        launchtime = parseLogs(logname) / 1000
        content = "index %d: %d s" % (index, launchtime)
        print content
        index += 1
        resList.append(launchtime)
    
    # prevent subprocess blocked
    adb.raw_cmd("kill-server").communicate()
    qalaunchtime.handleResult(caseName, resList, pwd)

# ----------------------------------------------------------------------------------------------------
doColdbootTime()


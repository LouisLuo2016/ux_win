#!/usr/bin/env python
import os
import sys
import re
import time
import json
import loghelper
from adb import adb

warm_launch = False
'''
cur = os.getcwd()
systrace = cur/systrace
logcat = cur/logcat
dmesg = cur/dmesg
'''

def removeFromLRU():
    adb.cmd("shell input keyevent 187").communicate()
    time.sleep(1)
    adb.cmd("shell input swipe 200 674 700 674 250").communicate()
    time.sleep(1)

def amstop(packageName):
    if packageName == "com.android.mms":
        ps = adb.cmd("shell ps | findstr %s" % packageName).communicate()
        r = re.match(r"(?P<head>u\w+)\s+(?P<pid>\d+)", ps[0])
        adb.cmd("shell kill %s" % r.group('pid')).communicate()
    else:
        # download process has alias
        if packageName == "com.android.providers.downloads.ui":
            packageName = "com.android.documentsui"
        adb.cmd("shell am force-stop %s" % packageName).communicate()
    time.sleep(2)

def dump_logcat(name):
    with open(name, "w") as f:
        f.write(adb.cmd("logcat -v threadtime -d").communicate()[0])

def clear_logcat():
    adb.cmd("logcat -c").communicate()

def dump_dmesg(name):
    with open(name, "w") as f:
        f.write(adb.cmd("shell dmesg").communicate()[0])

def getLaunchTime(logoutput):
    startpoint = 0
    endpoint = 0
    fd = open(logoutput, "r")
    logcatLogs = fd.readlines()
    for log in logcatLogs:
        logElement = loghelper.parse2Element(log, "logcat")
        if "ActivityManager" == logElement.tagName and "START" in logElement.tagContent:
            startpoint = logElement.ts
        elif "ActivityManager" == logElement.tagName and "Displayed" in logElement.tagContent:
            endpoint = logElement.ts
            
        if warm_launch:
            if "WindowManager" == logElement.tagName and "Changing focus from null to Window" in logElement.tagContent:
                endpoint = logElement.ts
    launchtime = endpoint - startpoint
    fd.close()
    return launchtime

def killproc(t, pname):
    if t not in ["lru", "amstop"]:
        raise ValueError("%s is not supported" % t)
    if t == "lru":
        removeFromLRU()
    elif t == "amstop":
        amstop(pname)
        
def handleResult(caseName, resList, pwd):
    sum = 0
    average = 0
    outfd = open("out.result", "w")
    outfd.write(caseName + "\n")
    for i in range(len(resList)):
        sum += resList[i]
        content = "index %d: %d ms" % (i, resList[i])
        outfd.write(content + "\n")
    average = sum / len(resList)
    content = "average: %d ms" % (average)
    print content
    outfd.write(content + "\n")

    resList.sort()
    median = resList[((len(resList) + 1) / 2) - 1]
    content = "median: %d ms" % (median)
    print content
    outfd.write(content + "\n")
    outfd.close()
    os.chdir(pwd)
    
    addReportData(caseName, median)
    
    
def addReportData(caseName, median):
    cf = "../../conf/args.json"
    conf = json.load(file(cf))
    value = conf.get(caseName, "None")
    if value == "None":
        conf[caseName] = median
        target = median
        json.dump(conf, open(cf, 'w'), sort_keys=True, indent=4)
    else:
        target = float(value)
    rep_data = "<tr><td>%s</td><td>%d(ms)</td><td>%d</td><td>%s</td><td>%s</td></tr>\n" \
    % (caseName, int(target), median, '10%', 'Pass' if ((median - target)/target < 0.1) else 'Fail')
    report = open('report.html', 'a')
    report.write(rep_data)
    report.close()

def doQALaunchTime(qaArgs):
    global warm_launch

    # get params
    duration = qaArgs.get("sleep_time")
    caseName = qaArgs.get("caseName")
    packageName = qaArgs.get("packageName")
    # componentName = qaArgs.get("cmpName")
    repeatCount = qaArgs.get("repeat")
    finishtype = qaArgs.get("finishtype", "amstop")
    time_for_stable = qaArgs.get("stabletime", 5)
    warm_launch = qaArgs.get("warm_launch", False)
    skip = qaArgs.get("skip", True)
    # lunchCmd = "shell am start -a android.intent.action.MAIN \
    # -c android.intent.category.LAUNCHER -n %s" % (componentName)
    lunchCmd = "shell monkey -p %s -c android.intent.category.LAUNCHER 1" % packageName

    # create work path
    pwd = os.getcwd()
    os.makedirs(caseName)
    os.chdir(caseName)
    
    resList = []
    index = 0
    content = caseName
    print content
    launchtime = 0
    logname = "logcat"

    if skip:
        adb.cmd(lunchCmd).communicate()
        # handle application permission
        time.sleep(duration)
        if caseName != "wallet":
            adb.cmd("shell input tap 515 1691").communicate()
        if not warm_launch:
            killproc(finishtype, packageName)
        else:
            adb.cmd("shell input keyevent 3").communicate()

    while (index < repeatCount):
        clear_logcat()
        adb.cmd(lunchCmd).communicate()
        time.sleep(duration)
        logname = "%s_%d.logcat" % (caseName, index)
        dump_logcat(logname)
        launchtime = getLaunchTime(logname)
        content = "index %d: %d ms" % (index, launchtime)
        print content
        index += 1
        resList.append(launchtime)
        if not warm_launch:
            killproc(finishtype, packageName)
        else:
            adb.cmd("shell input keyevent 3").communicate()

        time.sleep(time_for_stable)
    
    handleResult(caseName, resList, pwd)





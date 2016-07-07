#!/usr/bin/env python

import re
import os
import sys
import subprocess
import time

PARSE_DBG = False

class StraceElement():

    def __init__(self, ts, callname, fd, ret):
        self.ts = ts
        self.callname = callname
        self.fd = fd
        self.ret = ret

    def dump(self):
        print "%f %s(%s) = %s" % (self.ts, self.callname, self.fd, self.ret)

'''
equicksearchbox-2525  ( 2525) [000] ...1 10007.451469: tracing_mark_write: B|2525|activityPause\n\
'''
class TraceElement():
    ts = 0
    pid = 0
    flag = ""
    tagName = ""

    def __init__(self, ts, pid, flag, tagName):
        self.ts = ts
        self.pid = pid
        self.flag = flag
        self.tagName = tagName

    def dump(self):
        if self.ts == -1 or self.pid == -1 or self.flag == "wrong" or self.tagName == "wrong":
            return
        print ("ts: %d, pid = %d, flag: %s, tagName: %s") % (self.ts, self.pid, self.flag, self.tagName)

class DmesgElement():
    ts = 0
    content = ""

    def __init__(self, ts, content):
        self.ts = ts
        self.content = content

    def dump(self):
        print ("[%f] %s") % (self.ts, self.content)

class LogcatElement():
    ts = 0
    pid = 0
    tid = 0
    tagType = ""
    tagName = ""
    tagContent = ""

    def __init__(self, ts, pid, tid, tagType, tagName, tagContent):
        self.ts = ts
        self.pid = pid
        self.tid = tid
        self.tagType = tagType
        self.tagName = tagName
        self.tagContent = tagContent

    def dump(self):
        print self.ts
        print self.pid
        print self.tid
        print self.tagType
        print self.tagName
        print self.tagContent

def parse2Element(log, type):
    if type == "trace":
        return parse2TraceElement(log)
    elif type == "logcat":
        return parse2LogcatElement(log)
    elif type == "dmesg":
        return parse2DmesgElement(log)
    elif type == "strace":
        return parse2StraceElement(log)
    else:
        print "Error: unsupported type %s" % type
        sys.exit()
'''
pattern:
01-02 17:58:35.603  1982  2395 W SurfaceFlinger: Timed out waiting for hw vsync; faking it
'''
def parse2LogcatElement(logcatLog):
    r = re.match(r"\d+\-\d+\s(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\.(?P<milli>\d{3})\s+(?P<pid>\d+)\s+(?P<tid>\d+)\s+(?P<type>\S)\s+(?P<tag>\S+)\s*:\s+(?P<content>.*$)", logcatLog)
    if r is None:
        return LogcatElement(0, 0, 0, "", "", "")
    ts = (int(r.group("hour")) * 3600 + int(r.group("minute")) * 60 + int(r.group("second"))) * 1000 + int(r.group("milli"))
    return LogcatElement(ts, int(r.group("pid")), int(r.group("tid")), r.group("type"), r.group("tag"), r.group("content"))

'''
<6>[    0.115842] Last level dTLB entries: 4KB 128, 2MB 16, 4MB 16, 1GB 0
'''
def parse2DmesgElement(dmesgLog):
    r = re.match(r"(<\d+>)*\[(?P<ts>\s*\d+.\d+)\]\s(?P<content>.*$)", dmesgLog)
    if r is None:
        return DmesgElement(0, "wrong")
    return DmesgElement(float(r.group("ts")) * 1000, r.group("content"))

'''
surfaceflinger-179   (  179) [003] d..3   471.432013: sched_wakeup: comm=Binder_2 pid=198 prio=120 success=1 target_cpu=002\n\
surfaceflinger-179   (  179) [003] ...1   471.432036: tracing_mark_write: B|179|rebuildLayerStacks\n\
'''
def parse2TraceElement(traceLog):
    r = re.match(r"<*(?P<tname>\w+)-(?P<tid>\d+)\s+\(\s*(?P<pid>\d+)\)\s+\[(?P<cpuid>\d+)\]\s+.{4}\s+(?P<ts>\d+\.\d+):\s+(?P<type>\w+):\s+(?P<content>.*$)", traceLog)
    if r is None:
        return TraceElement(-1, -1, "wrong", "wrong")
    if r.group("type") == "tracing_mark_write":
        t = r.group("content").strip().split("|")
        return TraceElement(float(r.group("ts")) * 1000, int(r.group("pid")), t[0], t[-1])
    else:
        return TraceElement(-1, -1, "unsupported", "unsupported")

def parse2StraceElement(strace):
    strace = strace.strip()
    strace = strace.split("=")
    ret = int(strace[-1])
    leftcurve = strace[0].index("(")
    firstcomma = strace[0].index(",")
    fd = strace[0][leftcurve + 1: firstcomma]
    firstspace = strace[0].index(" ")
    callname = ""
    ts = 0
    if firstspace > leftcurve:
        '''means no ts'''
        callname = strace[0][:leftcurve]
        ts = 0
    else:
        callname = strace[0][firstspace + 1:leftcurve]
        ts = float(strace[0][:firstspace]) * 1000

    return StraceElement(ts, callname, fd, ret)
    
def writeVersionStatus(str):
    vf = open("newversion", 'w')
    vf.seek(0)
    vf.write(str)
    vf.close()
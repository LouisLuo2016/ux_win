#!/usr/bin/env python
import os
import subprocess
import sys
import time

import mail
import loghelper

from adb import adb
from BeautifulSoup import BeautifulSoup
from infocollector import collector as ic

def generate_report_head():
    # writ report head
    f = open('report.html', 'w')
    f.write("<html>\n<body>\n<table border=\"1\">\n<caption>Automatic Test Report</caption>\n")
    f.write("<tr><td colspan=\"5\"><p>Device: %s</p></td></tr>\n" % ic.board())
    f.write("<tr><td colspan=\"5\"><p>Release: %s</p></td></tr>\n" % ic.release())
    f.write("<tr><td colspan=\"5\"><p>FreeMemory: %s</p></td></tr>\n" % ic.available_mem())
    f.write("<tr><td colspan=\"5\"><p>Temperature: %s</p></td></tr>\n" % ic.temperature())
    f.write("<tr><th>Case</th><th>Target</th><th>Value</th><th>FluctuationRange</th><th>Verdict</th></tr>\n")
    f.close()

def generate_report_foot():
    # writ report foot
    f = open('report.html', 'a')
    f.write("</table>\n</body>\n</html>")
    f.close()

def task_executor():
    # creat work dir
    outDir = "%s/%s%s" % ('report', 'report', time.strftime('%Y%m%d-%H%M%S'))
    pwd = os.getcwd()
    os.makedirs(outDir)
    os.chdir(outDir)
    generate_report_head()

    fname = '%s/tasklist.xml' % pwd
    if os.path.exists(fname):
        with open(fname, "r") as f:
            soup = BeautifulSoup("\n".join(f.readlines()))
            l_node = soup.findAll('case')
            for node in l_node:
                d_attr = {}
                for key, val in node.attrs:
                    d_attr[key] = val
                args = []
                name = d_attr['name']
                args.append(name)
                args.append('-t %s' % d_attr['time'])
                args.append('-r %s' % d_attr['repeat'])
                if d_attr['skip'] == 'true':
                    args.append('-s')
                
                key = name[29:]
                task = " ".join(args)
                executor(key, task)
    else:
        print "%s not found in current folder" % fname
        sys.exit(1)
    
    generate_report_foot()
    # wipe off as " daemon not running" string
    ic.board()
    subject = "[Automatic Test Report][%s] - %s" % (ic.board(), ic.release())
    mail.send_email(subject)
    os.chdir(pwd)
    
def executor(key, task):
    if task == None:
        return
    print "%s start" % (key)
    start = time.time()
    cur_task = subprocess.Popen("python %s" % (task), shell=True, stderr=subprocess.PIPE, preexec_fn=None)
    out = cur_task.communicate()
    if out[1] == '':
        print "%s is success" % (key)
    else:
        print "%s is fail" % (key)
        print out[1]

def flashDevice(version):
    pwd = os.getcwd()
    os.chdir("image/%s" % version)
    result = False
    # delete pause cmd from the bat
    bat = open("le_zl1_fastboot.bat", "r")
    batlist = bat.readlines()
    for line in batlist:
        if "pause" in line:
            batlist.remove(line)
    bat.close()
    bat = open("le_zl1_fastboot.bat", "w")
    for line in batlist:
        bat.write(line)
    bat.close()
    
    print("===========================")
    print("fastbooting................")
    print("please waiting.............")
    print("===========================")
    fdout = open("flash.out", 'w')
    cur_task = subprocess.Popen("le_zl1_fastboot.bat", stdout=fdout, stderr=fdout, shell=True)
    cur_task.communicate()
    fdout.close()
    print("==first boot,wait 180s ====")
    time.sleep(180)
    out = adb.raw_cmd("wait-for-device").communicate()
    if out[1] == '':
        result = True
    else:
        result = False

    os.chdir(pwd)
    return result
        
def main():
    while 1:
        # Observe daily build
        subprocess.Popen("python lib/Download.py zl1", shell=True, stderr=subprocess.PIPE, preexec_fn=None).communicate()
        release = "eng.buildfarm.%s" % (time.strftime('%Y%m%d'))
        vf = open("newversion", 'r')
        line = vf.readline().split(':')
        vf.close()
        version = line[0]
        if line[1] == 'download':
            doit = True
            print "\nNew verison: %s\n" % version
            
            # Device release is not newversion, then flash device 
            if release not in ic.release():
                doit = False
                # Flash device
                for i in range(3):
                    if flashDevice(version):
                        doit = True
                        break
                    else:
                        loghelper.writeVersionStatus("%s:%s" % (version, 'fail'))
            
            if doit:
                # First, wakeup screen, set screen_off_timeout, disable setupwizard/keyguard
                adb.root()
                # prevent subprocess blocked
                adb.raw_cmd("wait-for-device").communicate()
                adb.cmd("shell input keyevent 82").communicate()
                adb.cmd("shell pm disable com.letv.android.setupwizard").communicate()
                adb.cmd("shell settings put system screen_off_timeout 1800000").communicate()
                adb.cmd("shell wm dismiss-keyguard").communicate()
                
                # executor test task
                task_executor()
                loghelper.writeVersionStatus("%s:%s" % (version, 'cmp'))
                    
if __name__ == '__main__':
    main()

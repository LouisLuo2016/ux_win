#!/usr/bin/env python
import sys
import qalaunchtime
from argparse import ArgumentParser
from adb import adb

p = ArgumentParser(usage='xxx_launch.py -t n -r n', description='Author louis')
p.add_argument('-t', default=5,  dest='sleep_time', type=int, help='sleep_time')
p.add_argument('-r', default=5,  dest='repeat', type=int, help='repeat')
p.add_argument('-w', action='store_true', dest='warm_launch')
p.add_argument('-s', action='store_true', dest='skip')
a = p.parse_known_args(sys.argv)

args = {}
args["repeat"] = a[0].repeat
args["sleep_time"] = a[0].sleep_time
args['warm_launch'] = a[0].warm_launch
args['skip'] = a[0].skip

def doAppLaunch():
    print "doAppLaunch"
    listPak = list(pak[8:] for pak in adb.cmd("shell pm list packages -e").communicate()[0].splitlines() if pak.strip())
    listPak.remove("com.android.stk")
    listPak.remove("com.android.mms.service")
    listPak.sort()
    noFind = "No activities found to run"
    # del no activities package
    for package in listPak:
        if noFind not in adb.cmd("shell monkey -p %s -c android.intent.category.LAUNCHER 1" % package).communicate()[0]:
            qalaunchtime.amstop(package)
            args["packageName"] = package
            args["caseName"] = package.split(".")[-1]
            try:
                qalaunchtime.doQALaunchTime(args)
                print "Launch %s success!" % package
            except Exception,e:
                print "Launch %s fail!" % package
                print e
        
        # prevent subprocess blocked
        adb.raw_cmd("kill-server").communicate()
    
    # package = "com.letv.wallet"
    # args["packageName"] = package
    # args["caseName"] = package.split(".")[-1]
    # try:
        # qalaunchtime.doQALaunchTime(args)
        # print "Launch %s success!" % package
    # except Exception,e:
        # print "Launch %s fail!" % package
        # print e
    
    # # prevent subprocess blocked
    # adb.raw_cmd("kill-server")
    
#--------------------------------------------------------------------------------------------------------------------------------------------
doAppLaunch()
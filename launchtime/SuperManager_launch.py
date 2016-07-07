#!/usr/bin/env python
import sys
from argparse import ArgumentParser

from infocollector import collector as ic
from qalaunchtime import doQALaunchTime

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
# ----------------------------------------------------------------------------------------------------


args["cmpName"] = "com.letv.android.supermanager/.activity.SuperManagerActivity"
args["packageName"] = "com.letv.android.supermanager"
args["caseName"] = "SuperManager_launch"
# ----------------------------------------------------------------------------------------------------
doQALaunchTime(args)
#!/usr/bin/env python
import os
import platform
import re
import sys
from argparse import ArgumentParser


def getArgs():
    args = {}
    caseName = raw_input("CaseName: ")
    packageName = raw_input("PackageName: ") 
    cmpName = raw_input("ComponentName: ")
    args["cmpName"] = cmpName
    args["packageName"] = packageName
    args["caseName"] = "%s_launch" % (caseName)
    return args


def writeHeader(outfd):
    path = "%s/%s" % (sys.path[0], "header")
    fd = open(path, "r")
    content = fd.readlines()
    for line in content:
        outfd.write(line)
    outfd.write("# %s\n" % ("-" * 100))


def writeArgs(outfd, args):
    for key in args.keys():
        line = "args[\"%s\"] = \"%s\"\n" % (key, str(args.get(key)))
        outfd.write(line)
    outfd.write("# %s\n" % ("-" * 100))
    outfd.write("doQALaunchTime(args)")


def update_scripts():
    l_script = []
    for p, d, f in os.walk(sys.path[0]):
        for py in f:
            if py[-2:] == "py" and py[-9:-3] == "launch":
                l_script.append(os.path.join(p, py))
    for script in l_script:
        arg_lines = []
        with open(script, "r") as f:
            t = f.readlines()
            arg_line_bound = []
            for i in xrange(len(t)):
                if t[i].strip() == "# %s" % ("-" * 100):
                    arg_line_bound.append(i)
            if arg_line_bound == []:
                continue
            arg_lines = t[arg_line_bound[0] + 1: arg_line_bound[1]]
        with open(script, "w") as f:
            writeHeader(f)
            for line in arg_lines:
                f.write(line)
            f.write("# %s\n" % ("-" * 100))
            f.write("doQALaunchTime(args)")


def main():
    p = ArgumentParser(usage='launch_script_generator.py [-u]', description='Author louis')
    p.add_argument('-u', action='store_true', dest='update')
    a = p.parse_known_args(sys.argv)
    if a[0].update:
        update_scripts()
        return 0
    args = getArgs()
    fn_script = "%s.py" % (args.get("caseName"))
    fd = open(fn_script, "w")
    writeHeader(fd)
    fd.write("\n")
    fd.write("\n")
    writeArgs(fd, args)
    fd.close()
    #cmd = "chmod +x %s " % fn_path
    #os.system(cmd)


if __name__ == '__main__':
    main()

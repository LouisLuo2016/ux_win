# -*- coding: utf8 -*-
import os
import sys
import time
import shutil
import loghelper
import json
from ftplib import FTP
pwd = os.getcwd()

conf = json.load(file("conf/args.json"))
username = conf["username"]
password = conf["password"]
ftpserver = conf["dailybuildFtp"]
beforeUrl = conf["beforeUrl"]
afterUrl = conf["afterUrl"]

def getNewVersion(deviceType):
    version = ""
    try:
        ftp = FTP(ftpserver, username, password)
        ftp.cwd(beforeUrl[deviceType])
        dir_res = []
        ftp.dir('.', dir_res.append)
        dirs = [f.split(None, 8)[-1] for f in dir_res if f.startswith('d')]
        dailybuild = "%s_zl_leui2.0_%s" % (time.strftime('%Y-%m-%d'), time.strftime('%Y'))
        for dir in dirs:
            if dailybuild in dir:
                version = dir
                break
        ftp.quit()
        return version
    except Exception,e:
        print("|||||||||||||||An unexpected error occurred when get new version!\n" + str(e))
        return version

def download(deviceType, version):
    imagedir = "image/" + version
    if os.path.exists(imagedir):
        return True
    else:
        os.makedirs(imagedir)
    image_url = "%s/%s%s" % (beforeUrl["zl1"], version, afterUrl["zl1"])
    try:        
        ftp = FTP(ftpserver, username, password)
        ftp.cwd(image_url)
        dir_res = []
        ftp.dir('.', dir_res.append)
        files = [f.split(None, 8)[-1] for f in dir_res if f.startswith('-')]

        print('================Download iamge Start!================')
        for f in files:
            outf = open("%s/%s" % (imagedir, f), 'wb')
            ftp.retrbinary('RETR %s' % f, outf.write)
            outf.close()
        ftp.quit()
        print('================Download iamge Success!================')
        return True
    except Exception,e:
        print("|||||||||||||||(%s)Download image failed!\n%s" % (version, str(e)))
        return False


    
if __name__=='__main__':
    deviceType = sys.argv[1]
    while 1:
        # newverison file content like "veriosn:status"
        dailybuild = "%s_zl_leui2.0_%s" % (time.strftime('%Y-%m-%d'), time.strftime('%Y'))
        vf = open("newversion", 'r')
        line = vf.readline().split(':')
        vf.close()
        needDownload = True
        if line[1] == 'new':
            version = line[0]
        elif line[1] == 'download':
            break
        elif line[1] == 'cmp' and dailybuild in line[0]:
            needDownload = False
            print "Not have new version!"
        else:
            version = getNewVersion(deviceType)
            if version == "":
                needDownload = False
                print "Not have new version!"
            else:
                loghelper.writeVersionStatus("%s:%s" % (version, 'new'))
                print "New version: %s" % (version)
        
        index = 0
        while (needDownload and index < 3):
            index += 1
            if download(deviceType, version):
                loghelper.writeVersionStatus("%s:%s" % (version, 'download'))
                break
            else:
                shutil.rmtree("image/" + version)
                loghelper.writeVersionStatus("%s:%s" % (version, 'fail'))
                
        print("Please wait 300S for next round to download...")
        for i in range(300):
            time.sleep(1)

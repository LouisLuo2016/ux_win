import subprocess
import os
import time


class Adb(object):

    def __init__(self, serial=None):
        self.__adb_exe = None
        self.canroot = True
        self.default_serial = serial if serial else os.environ.get("ANDROID_SERAIL", None)

    def adb(self):
        if self.__adb_exe is None:
            if "ANDROID_HOME" in os.environ:
                filename = "adb.exe" if os.name == "nt" else "adb"
                adb_exe = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", filename)
                if not os.path.exists(adb_exe):
                    raise EnvironmentError(
                            "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                import distutils
                if "spawn" not in dir(distutils):
                    import distutils.spawn
                adb_exe = distutils.spawn.find_executable("adb")
                if adb_exe:
                    adb_exe = os.path.realpath(adb_exe)
                else:
                    raise EnvironmentError("$ANDROID_HOME environment not set.")
            self.__adb_exe = adb_exe
        return self.__adb_exe

    def cmd(self, *args, **kwargs):
        '''adb command, add -s by default. return subprocess.Popen object.'''
        serial = self.device_serial()
        listargs = args[0].split(' ')
        if serial:
            if " " in serial:
                serial = "'%s'" % serial
            return self.raw_cmd(*["-s", serial] + listargs)
        else:
            return self.raw_cmd(listargs)

    def raw_cmd(self, *args):
        '''adb command return subprocess.Popen object.'''
        cmd_line = [self.adb()] + list(args)
        if os.name != "nt":
            cmd_line = [" ".join(cmd_line)]
        return subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=None)

    def device_serial(self):
        if not self.default_serial:
            devices = self.devices()
            if devices:
                if len(devices) is 1:
                    self.default_serial = list(devices.keys())[0]
                else:
                    raise EnvironmentError("Multiple devices attached but default android serial not set.")
            else:
                raise EnvironmentError("Device not attached.")
        return self.default_serial

    def devices(self):
        '''get a dict of attached devices. key is the device serail, value is device name.'''
        out = self.raw_cmd("devices").communicate()[0].decode("utf-8")
        match1 = "List of devices attached"
        match2 = "* daemon started successfully *"
        index1 = out.find(match1)
        if index1 < 0:
            raise EnvironmentError("adb is not working.")
        index2 = out.find(match2)
        index = index2 + len(match2) if index2 > 0 else index1 + len(match1)
        return dict([s.split("\t") for s in out[index:].strip().splitlines() if s.strip()])

    def getprop(self, key, t="str"):
        val = self.cmd("shell getprop %s" % key).communicate()[0].decode("utf-8")
        if t == "int":
            return int(val)
        elif t == "float":
            return float(val)
        else:
            return val.strip()

    def setprop(self, key, val):
        self.cmd("shell setprop %s %s" % (key, val))

    def root(self):
        if self.getprop("service.adb.root") == "1":
            return 0
        else:
            if self.canroot:
                self.cmd("root").communicate()
                self.cmd("wait-for-device").communicate()
                self.canroot = True if self.getprop("service.adb.root") == "1" else False
                if self.getprop("service.adb.root") == "0":
                    raise ValueError("Can't root")
                else:
                    return 0
            else:
                raise ValueError("Can't root")

    def checkpackage(self, package):
        info = self.cmd("shell 'dumpsys package %s'" % package).communicate()[0]
        return info != ""

    def getsysfs(self, path):
        out = self.cmd("shell cat %s" % path).communicate()[0].strip()
        return out

adb = Adb()

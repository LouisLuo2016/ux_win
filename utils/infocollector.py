from adb import Adb
from clog import colorlog as cl

freqtable = {
    "Z3735G": [1800, 1330],
    "Z3735F": [1800, 1330],
}
class InfoCollector(Adb):

    def board(self):
        return self.getprop("ro.board.platform")

    def release(self):
        return self.getprop("ro.build.version.incremental")

    def pversion(self, pname):
        out = self.cmd("shell dumpsys package %s" % pname).communicate()[0].decode('utf-8').splitlines()
        vname = ""
        for line in out:
            if "versionName" in line:
                vname = line.strip().split("=")[1]
                break
        if vname == "":
            raise ValueError("No package named %s" % pname)
        return vname

    def available_mem(self):
        out = self.cmd("shell cat /proc/meminfo").communicate()[0].decode('utf-8').splitlines()
        mem = -1
        for line in out:
            if "MemAvailable" in line:
                mem = float(line.split()[1]) / 1000.0
                break
        # if mem == -1:
            # raise ValueError("Can't get MemAvailable")
        return mem

    def cpu_name(self):
        out = self.cmd("shell cat /proc/cpuinfo").communicate()[0].decode('utf-8').splitlines()
        cpu_name = ""
        for line in out:
            if "model name" in line:
                t = line.strip().split()
                index_at = t.index("@")
                cpu_name = t[index_at - 1]
                break
        if cpu_name == "":
            raise ValueError("Can't get cpu name")
        return cpu_name

    def freq(self):
        out = self.cmd("shell cd /sys/devices/system/cpu/intel_pstate").communicate()[0].decode('utf-8')
        freq = 0
        if "No such file or directory" in out:
            out = self.cmd("shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq").communicate()[0].decode('utf-8')
            freq = int(out) / 1000
        else:
            no_turbo = int(self.cmd("shell cat /sys/devices/system/cpu/intel_pstate/no_turbo").communicate()[0].decode('utf-8'))
            max_perf_pct = int(self.cmd("shell cat /sys/devices/system/cpu/intel_pstate/max_perf_pct").communicate()[0].decode('utf-8'))
            freq = freqtable.get(self.cpu_name())[no_turbo] * max_perf_pct / 100
        if freq == 0:
            raise ValueError("Can't get freq")
        return freq

    def temperature(self):
        tempzone_count = 1
        temp = {}
        for i in xrange(tempzone_count):
            temp[i] = int(self.getsysfs("/sys/class/thermal/thermal_zone%d/temp" % i))
        total_temp = 0
        for t in temp.values():
            total_temp += t
        average = total_temp / tempzone_count / 1000
        if average > 50:
            cl.w("Temperatur is high(%d)" % average)
        return average

    def collect(self, pname):
        self.root()
        dic = {}
        try:
            dic["freq"] = self.freq()
        except:
            dic["freq"] = 0
        dic["board"] = self.board()
        dic["pname"] = self.pversion(pname)
        dic["rel"] = self.release()
        return dic

collector = InfoCollector()

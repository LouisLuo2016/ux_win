FORE_RED = 31
FORE_GREEN = 32
FORE_YELLOW = 33
FORE_BLUE = 34
FORE_PURPLE = 35
FORE_DARKGREEN = 36
FORE_WHITE = 37

def colorPrint(msg, color):
    fore = 37
    if (color == "red"):
        fore = FORE_RED
    elif (color == "green"):
        fore = FORE_GREEN
    elif (color == "yellow"):
        fore = FORE_YELLOW
    elif (color == "white"):
        fore = FORE_WHITE
    elif (color == "blue"):
        fore = FORE_BLUE
    elif (color == "purple"):
        fore = FORE_PURPLE
    elif (color == "dark_green"):
        fore = FORE_DARKGREEN
    else:
        print "Don't supprrot %s, use white as default" % color
    type = "\x1B[%d;%dm" % (0, fore)
    orig = "\x1B[0m"
    print "%s%s%s" % (type, msg, orig)


class clog:
    CLOG_LEVEL_VERSE = 1
    CLOG_LEVEL_DEBUG = 1 << 1
    CLOG_LEVEL_WARNING = 1 << 2
    CLOG_LEVEL_ERROR = 1 << 3
    CLOG_LEVEL_CRITICAL = 1 << 4
    CLOG_LEVEL = 1
    def v(self, str):
        if self.CLOG_LEVEL & self.CLOG_LEVEL_VERSE != 0:
            str = "Verse: %s" % str
            colorPrint(str, "green")
    def d(self, str):
        if self.CLOG_LEVEL & self.CLOG_LEVEL_DEBUG != 0:
            str = "Debug: %s" % str
            colorPrint(str, "blue")
    def w(self, str):
        if self.CLOG_LEVEL & self.CLOG_LEVEL_WARNING != 0:
            str = "Warn: %s" % str
            colorPrint(str, "yellow")
    def e(self, str):
        if self.CLOG_LEVEL & self.CLOG_LEVEL_ERROR != 0:
            str = "Error: %s" % str
            colorPrint(str, "red")
    def c(self, str):
        if self.CLOG_LEVEL & self.CLOG_LEVEL_CRITICAL != 0:
            str = "Critical: %s" % str
            colorPrint(str, "purple")
    def setLevel(self, str):
        args = str.strip().split("|")
        for arg in args:
            if arg == "v":
                self.CLOG_LEVEL |= self.CLOG_LEVEL_VERSE
            elif arg == "d":
                self.CLOG_LEVEL |= self.CLOG_LEVEL_DEBUG
            elif arg == "w":
                self.CLOG_LEVEL |= self.CLOG_LEVEL_WARNING
            elif arg == "e":
                self.CLOG_LEVEL |= self.CLOG_LEVEL_ERROR
            elif arg == "c":
                self.CLOG_LEVEL |= self.CLOG_LEVEL_CRITICAL
            else:
                print arg + "is not supported"
colorlog = clog()
colorlog.setLevel("v|e|c|w")

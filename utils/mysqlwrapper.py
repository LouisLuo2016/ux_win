import os
MYSQL = False
if os.environ.get("uxsql") == "MySQLdb":
    import MySQLdb
    MYSQL = True


def addquote(s):
    if isinstance(s, basestring):
        return "\"%s\"" % s
    else:
        return str(s)

class MySQLdbWrapper():

    def __init__(self):
        global MYSQL
        if MYSQL is True:
            conn = MySQLdb.connect(host='louis-wow', user='root', passwd='1', port=3306)
            cur = conn.cursor()
            conn.select_db("ux")
            self.cur = cur
            self.conn = conn

    def insert(self, table, kargs):
        if not MYSQL:
            return
        cmd = "insert into %s (%s) values(%s)" % (table, ", ".join(kargs.keys()), ", ".join(map(addquote, kargs.values())))
        self.cur.execute(cmd)
        self.conn.commit()

    def close(self):
        if not MYSQL:
            return
        self.cur.close()
        self.conn.close()

    def dump(self, table):
        if not MYSQL:
            return
        fd = open("%s/Documents/%s.csv" % (os.environ.get("HOME"), table), "w")
        cmd = "select * from %s" % table
        self.cur.execute(cmd)
        records = self.cur.fetchall()
        for r in records:
            fd.write(",".join(map(str, r[1:])))
            fd.write("\n")
        fd.close()


wrapper = MySQLdbWrapper()

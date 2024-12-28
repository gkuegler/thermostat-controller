from pg import DB
import os
import time

CREDENTIAL_NAME = "creds.txt"
CREDENTIAL_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   CREDENTIAL_NAME)

"""
Not specifying a 'host' defaults to unix sockets which is connection type 'local'.
"""
class SQL:
    def __init__(self, dbname, port=5432, use_creds=False) -> None:
        if use_creds:
            with open(CREDENTIAL_FILENAME, 'rt') as f:
                user = f.readline().strip(' \n')
                pw = f.readline().strip(' \n')
        else:
            user = "postgres"
            pw = None

        # self.tablename = tablename

        # Connect to DB
        self.db = DB(dbname=dbname, port=port, user=user, passwd=pw)

        # if not db.has_table_privilege(self.tablename, "insert"):
        #     raise RuntimeError(f"No SQL INSERT priviliges on table {self.tablename}")

    def insert(self, table, t=None, rh=None, sp=None, mode=None):
        # now = time.localtime()
        # f = '%Y-%m-%d %H:%M:%S'
        # print(time.strftime(f, now))
        # INSERT INTO test2 VALUES (CAST('2024-12-28 15:52:13 EST' AS TIMESTAMP WITH TIME ZONE), 67.35, 46.2);
        # self.db.query(INSERT INTO test2 VALUES (CAST('2024-12-28 15:52:13 EST' AS TIMESTAMP WITH TIME ZONE), 67.35, 46.2);
        t = 'NULL' if t == None else t
        rh = 'NULL' if rh == None else rh
        sp = 'NULL' if sp == None else sp
        mode = 'NULL' if mode == None else mode
        self.db.query(
            f"INSERT INTO {table} VALUES ('now', {t}, {rh}, {sp}, '{mode}');")

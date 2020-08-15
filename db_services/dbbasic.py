#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filename           : dbbasic.py
Author             : Inspiring Lab
Version            : 1.0
Date created       : 2017-01-05
Date last modified : 2017-07-07
Python Version     : 2.7
Description        : This is a script for basic database connection to PostgreSQL.
"""

import sys
import psycopg2 as pgsql
from pandas import DataFrame


"""Class to connect Postgres DB"""

class Connect():
    # Constructor
    def __init__(self, dbname, username, passwd, hostname, sport=5432, racflag=False):
        self.dbname = dbname
        self.username = username
        self.passwd = passwd
        self.hostname = hostname
        self.sport = sport
        self.racflag = racflag

    # Connect with tnscon string
    def tns_connect(self):
        try:
            conn = pgsql.connect(database=self.dbname, user=self.username, password=self.passwd, host=self.hostname,
                                 port=self.sport)
        except:
            print ("Unexpected error:", sys.exc_info(), "Function name:", self.__name__)
            # return Exception
        else:
            return conn


"""Class to execute different Postgres statements"""


class Execute():
    ##Constructor
    def __init__(self, con):
        self.con = con
        self.cursor = self.con.cursor()
        # self.statement=statement

    ##execute pgsql statement
    def execute_statement(self, statement):
        try:
            self.cursor.execute(statement)
        except pgsql.Error as e:
            # error,=e.args
            print ("Code:", e.pgcode)
            print ("Message:", e.pgerror)
            print (sys.exc_info(), "Function name:execute_statement")
            self.con.rollback()
        else:
            self.con.commit()
            # self.cursor.close()
            return self.cursor

    ##execute oracle statement using bind vars
    def execute_statement_bind(self, statement, bindvars):
        try:
            output = self.cursor.execute(statement, bindvars)
        except pgsql.Error as e:
            # error,=e.args
            print ("Code:", e.pgcode)
            print ("Message:", e.pgerror)
            print (sys.exc_info(), "Function name:execute_statement")
            self.con.rollback()
        else:
            self.con.commit()
            # self.cursor.close()
            return bindvars['sn']

    def execute_function(self, *args, **kwargs):
        funct_args = []
        for a in args:
            # print a
            funct_args.append(a)
        for k, v in kwargs.iteritems():
            print ("%s =%s" % (k, v))
            if k == "function_name":
                functname = v
        try:
            print ("Function name:", functname, "Function Args:", funct_args)
            # logger.info("Procedure arguments:"+proc_args)
            output = self.cursor.callproc(functname, funct_args)
            # output=output.fetchall()
        except:
            print ("Function error", sys.exc_info())
            return False
        else:
            self.con.commit()
            return int(output)

    def execute_proc(self, *args, **kwargs):
        proc_args = []
        for a in args:
            print (a)
            proc_args.append(a)
        for k, v in kwargs.iteritems():
            print ("%s =%s" % (k, v))
            if k == "proc_name":
                procname = v
        try:
            print ("Proc Args:", proc_args)
            # logger.info("Procedure arguments:"+proc_args)
            self.cursor.callproc(procname, proc_args)
        except:
            print ("Procedure error")
            return False
        else:
            self.con.commit()
            return True

    def excute_spool(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k == "bulkid":
                bulkid = v
            elif k == "spoolname":
                spoolname = v
            elif k == "query":
                query = v
        # stat="SELECT "
        output = self.execute_statement(query)
        return output

    def close(self):
        self.cursor.close()


class Trimstrdb():
    def trimdb(self, inputstr, trimlen=3999):
        self.trimstr = inputstr[0:trimlen]
        self.trimstr = self.trimstr.replace("'", "''")
        return self.trimstr


class Dbexecute():
    def __init__(self, conn):
        self.conn = conn
        self.trimstrobj = Trimstrdb()

    def retrieve_info(self, query):

        cur = self.conn.cursor()
        try:
            cur.execute(query)
            data = cur.fetchall()
            self.conn.commit()
            self.conn.close()
        except:
            print ("Unexptected error function:", sys.exc_info())
            return False

        return data

    def update_table_info(self, query):

        exestat = Execute(self.conn)
        try:

            exestat.cursor.execute(query)

            self.conn.commit()
            exestat.close()
        except:
            print ("Unexpected error function insertInfo:", sys.exc_info())
            return False
        else:
            return True

    def execute_query(self, query):
        exestat = Execute(self.conn)
        exestat.cursor.execute(query)
        self.conn.commit()
        exestat.close()
        return True

    # return data as pandas dataframe object
    def receive_db_data(self, query):

        cur = self.conn.cursor()
        try:
            cur.execute(query)
            data = cur.fetchall()
            cols = list(map(lambda x: x[0], cur.description))
            df = DataFrame(data, columns=cols)
            self.conn.commit()
            self.conn.close()
        except:
            print ("Unexptected error function:", sys.exc_info())
            print ("Returning empty dataframe")
            return DataFrame()

        return df

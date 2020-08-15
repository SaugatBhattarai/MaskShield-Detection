#!/usr/bin/python
try:
    import dbbasic
except:
    from . import dbbasic

# Database Config file for movie_poster
DB_NAME = "movie_poster_db"
DB_USERNAME = "movie_poster"
DB_PASSWORD = "movie_poster"
DB_HOSTNAME = "localhost"
DB_PORT = 5432
DB_RACFLAG = False


def dbconnect():
    pgsql_conn = dbbasic.Connect(
        DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DB_RACFLAG)
    conn = pgsql_conn.tns_connect()
    d1 = dbbasic.Dbexecute(conn)
    return d1


def dbconnect_cur():
    pgsql_conn = dbbasic.Connect(
        DB_NAME, DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DB_RACFLAG)
    conn = pgsql_conn.tns_connect()
    cur = conn.cursor()
    cur.execute("BEGIN")
    return cur

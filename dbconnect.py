import MySQLdb
def connection():
    conn=MySQLdb.connect(host='localhost',user='root',passwd='',db='eventmanagement',)
    c=conn.cursor()
    return c,conn

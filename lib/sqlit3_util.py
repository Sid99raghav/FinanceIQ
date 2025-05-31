#!/usr/bin/env python3
import sqlite3
import datetime
import traceback
import os
import sys
from inspect import currentframe, getframeinfo

# https://stackoverflow.com/questions/26286203/custom-print-function-that-wraps-print
def sql3_print(*args, **kwargs):
   print( "> "+" ".join(map(str,args)) + "", **kwargs)

def sql3_execute(database_path, cmd, params=None):
    """
    Execute an SQLite query with optional parameters.
    """
    print(f"Executing query: {cmd} with params: {params}")
    try:
        con = sqlite3.connect(database_path)
        cur = con.cursor()
        if params:
            cur.execute(cmd, params)  # Use parameterized query
        else:
            cur.execute(cmd)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        con.commit()
        con.close()
    except sqlite3.Error as er:
        sql3_print('SQLite error: %s' % (' '.join(er.args)))
        sql3_print("Exception class is: ", er.__class__)
        sql3_print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        sql3_print(traceback.format_exception(exc_type, exc_value, exc_tb))
        frameinfo = getframeinfo(currentframe())
        sql3_print(frameinfo.filename, frameinfo.lineno)

def sql3_get_len_records(database_path, cmd):
   print (cmd)
   cnt=0
   try:
       con = sqlite3.connect(database_path)
       cur = con.cursor()
       cur.execute(cmd)
       rows = cur.fetchall()
       cnt = len(rows)
       con.close()
   except sqlite3.Error as er:
       sql3_print('SQLite error: %s' % (' '.join(er.args)))
       sql3_print("Exception class is: ", er.__class__)
       sql3_print('SQLite traceback: ')
       exc_type, exc_value, exc_tb = sys.exc_info()
       sql3_print(traceback.format_exception(exc_type, exc_value, exc_tb))
   return cnt

def sql3_get_record(database_path, cmd):
   json_str = []
   try:
       con = sqlite3.connect(database_path)
       #import pdb;pdb.set_trace()
       cur = con.cursor()
       cur.execute(cmd)
       rows = cur.fetchall()
       json_str = [dict((cur.description[i][0], value)\
               for i, value in enumerate(r)) for r in rows]
       con.commit()# save and close
       con.close()
   except sqlite3.Error as er:
       sql3_print('SQLite error: %s' % (' '.join(er.args)))
       sql3_print("Exception class is: ", er.__class__)
       sql3_print('SQLite traceback: ')
       exc_type, exc_value, exc_tb = sys.exc_info()
       sql3_print(traceback.format_exception(exc_type, exc_value, exc_tb))
   print (type(json_str))
   return json_str

def sql3_init_db(database_path, create_table_query):
    if not os.path.isfile(database_path):
        os.makedirs(os.path.dirname(database_path), exist_ok = True)
    print ("Init DB")
    sql3_execute(database_path, create_table_query)  

def sql3_epoch(dt = None):
   if dt is None:
       return int(datetime.datetime.now().strftime('%s'))
   else:
       return int(dt.strftime('%s'))


# http://www.sqlite.org/draft/lang_upsert.html
def sql3_upsert(database_path, dd):
    if sql3_get_len_records(database_path, dd['find']) == 0:
       sql3_print(" should be an insert")
       sql3_execute(database_path, dd['insert']) 
    else:
       sql3_print(" should be an update")
       sql3_execute(database_path, dd['modify']) 

def sql3_delete(dd):
    sql3_execute(dd['delete'])

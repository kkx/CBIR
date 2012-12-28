"""
import sqlite3
import os
import time
con = sqlite3.connect('sqlite_database')

con.execute("create table if not exists word_record(code_id integer, image_id integer, dx REAL, dy REAL)")
start = time.time()
con.execute("create index if not exists icode_id on word_record(code_id)")
print end- start
end = time.time()
con.execute("create index if not exists iimage_id on word_record(image_id)")
print time.time() - end
end = time.time()
con.commit()
print time.time() - end
exit(1)

f_names = ["./book_cover_image_codes.txt_1_9", "./book_cover_image_codes.txt_2_14",\
        "./book_cover_image_codes.txt_3_10", "./book_cover_image_codes.txt_4_10",\
        "./book_cover_image_codes.txt_5_10", "./book_cover_image_codes.txt_6_10",\
        "./book_cover_image_codes.txt_7_10"]#, "./book_cover_image_codes.txt_2_14",\
        #"./book_cover_image_codes.txt_1_9", "./book_cover_image_codes.txt_2_14"]


print "inserting"
for f_name in f_names[:]:
    print f_name
    f = open(f_name,"r")
    count = 0
    time_count = time.time()
    for line in f:
        count += 1
        if count % 100000 == 0:
            final_count = time.time()
            print count, final_count - time_count
            time_count = final_count
        image_id,code_id, dx,xy = line.split()
        con.execute("insert into word_record values(%s, %s, %s, %s)"%(code_id,image_id,dx,xy))
    f.close()
    print "committing"
    va = time.time()
    con.commit()
    print "committed", time.time()-va



    # Print the table contents
    start2 = time.time()
    for row in con.execute("select * from word_record where image_id = 63717"):
            #print row
            pass

    start = time.time()
    for row in con.execute("select * from word_record where code_id = 24138207"):
            #print row
            pass

    print time.time() - start
    print start - start2
"""

import os
import MySQLdb
import time
conn=MySQLdb.connect(host="localhost",user="root",passwd="xxxxxx",db="book_cover",charset="utf8")
cur = conn.cursor()
cur.execute("create table if not exists word_record(code_id integer, image_id integer, dx REAL, dy REAL)")
cur.execute("CREATE INDEX if not exists code_id  ON word_record(code_id);")

f_names = ["./book_cover_image_codes.txt_1_9", "./book_cover_image_codes.txt_2_14",\
        "./book_cover_image_codes.txt_3_10", "./book_cover_image_codes.txt_4_10",\
        "./book_cover_image_codes.txt_5_10", "./book_cover_image_codes.txt_6_10",\
        "./book_cover_image_codes.txt_7_10", "./book_cover_image_codes.txt_8_10",\
        "./book_cover_image_codes.txt_9_10", "./book_cover_image_codes.txt_10_10"]


print "inserting"
for f_name in f_names[2:]:
    print f_name
    f = open(f_name,"r")
    count = 0
    time_count = time.time()
    for line in f:
        count += 1
        if count % 100000 == 0:
            final_count = time.time()
            print count, final_count - time_count
            time_count = final_count
        image_id,code_id, dx,xy = line.split()
        cur.execute("insert into word_record values(%s, %s, %s, %s)"%(code_id,image_id,dx,xy))
    f.close()
    print "committing"
    va = time.time()
    #con.commit()
    print "committed", time.time()-va



    # Print the table contents
    start2 = time.time()
    #for row in cur.execute("select * from word_record where image_id = 63717"):
    #        #print row
    #        pass

    start = time.time()
    cur.execute("select * from word_record where code_id = 24138207")
    for row in cur.fetchall():
            #print row
            pass

    print time.time() - start
    print start - start2


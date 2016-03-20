#!/usr/bin/env python
#coding: utf-8
import MySQLdb

# 打开数据库连接
db = MySQLdb.connect(host="localhost",user="root",passwd="root",db="pythontest",port=3306,charset="utf8")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# 如果数据表已经存在使用 execute() 方法删除表。
cursor.execute("DROP TABLE IF EXISTS EMPLOYEE")

# 创建数据表SQL语句
sql = """CREATE TABLE EMPLOYEE (
         FIRST_NAME  CHAR(20) NOT NULL,
         LAST_NAME  CHAR(20),
         AGE INT,
         SEX CHAR(1),
         INCOME FLOAT )"""

cursor.execute(sql)


# SQL 插入语句
sql = "INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME) VALUES ('Mac', 'Mohan', 20, 'M', 2000)"
try:
   # 执行sql语句
   cursor.execute(sql)
   # 提交到数据库执行
   db.commit()
except:
   # Rollback in case there is any error
   db.rollback()


# SQL 插入语句
sql = "INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME) VALUES ('%s', '%s', '%d', '%c', '%d' )" % ('Mac', 'Mohan', 20, 'M', 2000)
try:
   # 执行sql语句
   cursor.execute(sql)
   # 提交到数据库执行
   db.commit()
except:
   # 发生错误时回滚
   db.rollback()


records = list()
for i in xrange(20):
    records.append(('Mac', 'Mohan', int(20), 'M', int(2000)))

# 使用cursor()方法获取操作游标
cursor = db.cursor()

try:
    records_num = cursor.executemany("INSERT INTO EMPLOYEE(FIRST_NAME, LAST_NAME, AGE, SEX, INCOME) VALUES (%s, %s, %s, %s, %s)", records)  # The format string is not really a normal Python format string. You must always use %s for all fields.
    print records_num
    db.commit()
except Exception, e:
    print e
    db.rollback()



# fetchone(): 该方法获取下一个查询结果集。结果集是一个对象
# fetchall():接收全部的返回结果行.
# rowcount: 这是一个只读属性，并返回执行execute()方法后影响的行数。

# SQL 查询语句
sql = "SELECT * FROM EMPLOYEE WHERE INCOME > '%d'" % (1000)
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()  # 从当前cursor位置获取余下的可用结果
    for row in results:
        fname = row[0]
        lname = row[1]
        age = row[2]
        sex = row[3]
        income = row[4]
        # 打印结果
        print "fname=%s,lname=%s,age=%d,sex=%s,income=%d" % (fname, lname, age, sex, income)

    cursor.scroll(-2)  # 指针往上移2行。scroll(self, value, mode='relative'):移动指针到某一行。如果mode='relative',则表示从当前所在行移动value条，如果mode='absolute'，则表示从结果集的第一行移动value条.
    for row in cursor.fetchall():
        print row

except:
   print "Error: unable to fecth data"



# SQL 更新语句
sql = "UPDATE EMPLOYEE SET AGE = AGE + 1 WHERE SEX = '%c'" % ('M')
try:
   # 执行SQL语句
   cursor.execute(sql)
   # 提交到数据库执行
   db.commit()
except:
   # 发生错误时回滚
   db.rollback()

cursor.close()
# 关闭数据库连接
db.close()

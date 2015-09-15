## GROUP BY ##
### Attention ###
1. select中的字段，要么出现在group by后面作为分组的依据，要么出现在select后面的聚合函数中。  
 
 Example:
 
 ```sql
select 类别, sum(数量) as 数量之和, 摘要
from A
group by 类别
order by 类别 desc
```
 
 Error:  
 ![group by error](http://i.imgur.com/2mEmKtg.png)

2. where和having的区别：
 - having一般用在group by之后，并且也是在group by起作用之后having才起作用的，where是在group by起作用之前就开始起作用的。having中经常包含聚合函数。  
 
 Example:  

 ```sql
select 类别, SUM(数量)from A
where 数量 > 8
group by 类别
having SUM(数量) > 10
```

 先筛选出数量 > 8的那些列，然后对这些列进行按类别的group by，然后在group by的结果基础上，再进行having操作，筛选出sum(数量) > 10的那些结果。

### JOIN ###

```sql
id name       id  name
-- ----      --  ----
1  Pirate     1   Rutabaga
2  Monkey     2   Pirate
3  Ninja      3   Darth Vader
4  Spaghetti  4   Ninja
```

1. **内连接**  
 默认是内连接，结果为俩表的交集，即可以省略inner关键字。
 
 ```sql
 SELECT * FROM TableA
INNER JOIN TableB
ON TableA.name = TableB.name
id  name       id   name
--  ----      --   ----
1   Pirate     2    Pirate
3   Ninja      4    Ninja
```
 
2. **外连接**  

 - **左外连接**  
  结果为左表全部，右表符合条件。右表不符合条件的地方会置为null。
  
  ```sql
  SELECT * FROM TableA
LEFT OUTER JOIN TableB
ON TableA.name = TableB.name
id  name       id    name
--  ----       --    ----
1   Pirate     2     Pirate
2   Monkey     null  null
3   Ninja      4     Ninja
4   Spaghetti  null  null
```

 - **右外连接**  
  结果为右表全部，左表符合条件。左表不符合条件的地方会置为null。
 - **全外连接**  
  结果和内连接对应，为俩表的并集(并非数学概念上的并集，这里为符合条件的并)。
  
  ```sql
 SELECT * FROM TableA
FULL OUTER JOIN TableB
ON TableA.name = TableB.name
id    name       id    name
--    ----       --    ----
1     Pirate     2     Pirate
2     Monkey     null  null
3     Ninja      4     Ninja
4     Spaghetti  null  null
null  null       1     Rutabaga
null  null       3     Darth Vader
```

##explain select 语句##
explain 可以分析后面的select语句的执行情况

```sql
mysql> explain select * from pre_common_member where email like '1%'\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: pre_common_member
         type: range
possible_keys: email
          key: email
      key_len: 120
          ref: NULL
         rows: 4
        Extra: Using index condition
1 row in set (0.00 sec)
```

```
id:表示select语句的编号
select_type:表示select语句的类型
    常用取值：
        SIMPLE表示简单查询，不包括连接查询和子查询
        primary表示主查询，或者最外层的查询语句
        union表示连接查询的第二个或后面的查询语句
table:表示查询的表
type:表示表的连接查询
    常用取值：
        const表示表中有多条记录，但是表中只查询一条记录
        all表示对表进行了完整的扫描
        eq_ref表示多表连接，后面的表使用了UNIQUE或者primary key;
        ref表示多表查询时，后面的表使用了普通索引。
        unique_subquery表示子查询中使用了普通索引；
        range表示查询语句中给出了查询范围；
        index表示对表中的索引进行了完整的扫描
possible_keys:查询中可能使用的索引
key:表示查询使用到的索引
key_len:索引字段的长度
ref:表示使用哪个列或常数与索引一起来查询记录
rows:表示查询到的行数；
extra:表示查询过程中的附加信息
```

##单列索引和组合索引##
MySQL单列索引是我们使用MySQL数据库中经常会见到的，MySQL单列索引和组合索引的区别可能有很多人还不是十分的了解，下面就为您分析两者的主要区别，供您参考学习。

为了形象地对比两者，再建一个表：

```sql
CREATE TABLE myIndex ( i_testID INT NOT NULL AUTO_INCREMENT, vc_Name VARCHAR(50) NOT NULL, vc_City VARCHAR(50) NOT NULL, i_Age INT NOT NULL, i_SchoolID INT NOT NULL, PRIMARY KEY (i_testID) ); 
```

在这 10000 条记录里面 7 上 8 下地分布了 5 条 vc_Name="erquan" 的记录，只不过 city,age,school 的组合各不相同。  

来看这条T-SQL：

```sql
SELECT i_testID FROM myIndex WHERE vc_Name='erquan' AND vc_City='郑州' AND i_Age=25; 
```

首先考虑建MySQL单列索引：

在vc\_Name列上建立了索引。执行 T-SQL 时，MYSQL <font color="red">很快将目标锁定在了vc\_Name=erquan 的 5 条记录上</font>，取出来放到一中间结果集。在这个结果集里，先排除掉 vc\_City 不等于"郑州"的记录，再排除 i\_Age 不等于 25 的记录，最后筛选出唯一的符合条件的记录。

虽然在 vc\_Name 上建立了索引，查询时MYSQL不用扫描整张表，效率有所提高，但离我们的要求还有一定的距离。同样的，在 vc\_City 和 i\_Age 分别建立的MySQL单列索引的效率相似。

为了进一步榨取 MySQL 的效率，就要考虑建立组合索引。就是将 vc\_Name,vc\_City，i\_Age 建到一个索引里：

```sql
ALTER TABLE myIndex ADD INDEX name_city_age (vc_Name(10),vc_City,i_Age); 
```

建表时，vc\_Name 长度为 10，这里为什么用 10 呢？因为一般情况下名字的长度不会超过 10，这样会加速索引查询速度，还会减少索引文件的大小，提高 INSERT 的更新速度。
执行 T-SQL 时，MySQL 无须扫描任何记录就到找到唯一的记录。

肯定有人要问了，<font color="red">如果分别在 vc\_Name,vc\_City，i\_Age 上建立单列索引，让该表有 3 个单列索引，查询时和上述的组合索引效率一样吗？</font>大不一样，远远低于我们的组合索引。虽然此时有了三个索引，但 MySQL 只能用到其中的那个它认为似乎是最有效率的单列索引。

建立这样的组合索引，其实是相当于分别建立了

```sql
vc_Name,vc_City,i_Age  
vc_Name,vc_City  
vc_Name 
```

这样的三个组合索引！为什么没有 vc\_City，i\_Age 等这样的组合索引呢？这是因为 mysql 组合索引“<font color="red">最左前缀</font>”的结果。简单的理解就是只从最左面的开始组合。并不是只要包含这三列的查询都会用到该组合索引，下面的几个 T-SQL 会用到：

```sql
SELECT * FROM myIndex WHREE vc_Name="erquan" AND vc_City="郑州" 
SELECT * FROM myIndex WHREE vc_Name="erquan" 
```

而下面几个则不会用到：

```sql
SELECT * FROM myIndex WHREE i_Age=20 AND vc_City="郑州" 
SELECT * FROM myIndex WHREE vc_City="郑州" 
```

##SQL注入与MyBatis##
###SQL注入###
如果用户执行：

```sql
select * from product where id = 5
```

这条语句。其中5是有用户输入的。

SQL注入的含义就是，一些捣蛋用户输入的不是5，而是

```sql
5; delete from orders
```

那么原来的SQL语句将会变为，

```sql
select * from product where id=5; delete from orders
```
在执行完select后，还将删除orders表里的所有记录。（如果他只删了这些记录，已经谢天谢地了，他可能会做更可怕地事情）。

不过庆幸的是，Ibatis使用的是预编译语句（PreparedStatements ）。

上述语句会被编译为，

```sql
select * from product where id=? 
```

从而有效防止SQL注入。

不过当你使用$占位符时就要注意了。

例如：动态的选择列和表

```sql
SELECT * FROM $TABLE_NAME$ WHERE $COLUMN_NAME$ = #value# 
```
这时你一定要仔细过滤那些值以避免SQL注入。当然这种情况不只存在Ibatis中。

###占位符的注入解决###
iBatis解决sql注入

1. ibatis xml配置：下面的写法只是简单的转义 name like '%\$name\$%'
2. 这时会导致sql注入问题，比如参数name传进一个单引号“'”，生成的sql语句会是：name like '%'%'
3. 解决方法是利用字符串连接的方式来构成sql语句 name like '%'||'\#name\#'||'%'
4. 这样参数都会经过预编译，就不会发生sql注入问题了。
5. \#与\$区别:

 > - \#xxx\# 代表xxx是属性值，map里面的key或者是你的pojo对象里面的属性, ibatis会自动在它的外面<font color="red">加上引号</font>，表现在sql语句是这样的 where xxx = 'xxx' ;

 > - \$xxx\$ 则是把xxx作为字符串拼接到你的sql语句中, 比如 order by topicId , 语句这样写 ... order by \#xxx\#，ibatis 就会把他翻译成 order by 'topicId' （这样就会报错） 语句这样写 ... order by \$xxx\$，ibatis 就会把他翻译成 order by topicId；

##注意##
1. \#将传入的数据都当成一个字符串，会对自动传入的数据加一个双引号。如：order by \#user\_id\#，如果传入的值是111,那么解析成sql时的值为order by "111", 如果传入的值是id，则解析成的sql为order by "id"。
2. \$将传入的数据直接显示生成在sql中。如：order by \$user\_id\$，如果传入的值是111,那么解析成sql时的值为order by user\_id, 如果传入的值是id，则解析成的sql为order by id.
3. \#方式能够很大程度防止sql注入。
4. \$方式无法防止Sql注入。
5. \$方式一般用于传入数据库对象，例如传入表名。
6. 一般能用\#的就别用\$。

MyBatis排序时使用order by 动态参数时需要注意，用$而不是#
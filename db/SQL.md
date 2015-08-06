## GROUP BY ##
> ### Attention ###
>> 1. select中的字段，要么出现在group by后面作为分组的依据，要么出现在select后面的聚合函数中。  
>> Example:<pre>
<code>select 类别, sum(数量) as 数量之和, 摘要
from A
group by 类别
order by 类别 desc
</code></pre>
>> Error:  
>> ![group by error](http://i.imgur.com/2mEmKtg.png)
>> 2. where和having的区别：  
>> having一般用在group by之后，并且也是在group by起作用之后having才起作用的，where是在group by起作用之前就开始起作用的。having中经常包含聚合函数。  
>> Example:<pre><code>select 类别, SUM(数量)from A
where 数量 > 8
group by 类别
having SUM(数量) > 10
</code></pre>
>> 先筛选出数量 > 8的那些列，然后对这些列进行按类别的group by，然后在group by的结果基础上，再进行having操作，筛选出sum(数量) > 10的那些结果。

> ### JOIN ###
> <pre><code>id name       id  name
-- ----      --  ----
1  Pirate     1   Rutabaga
2  Monkey     2   Pirate
3  Ninja      3   Darth Vader
4  Spaghetti  4   Ninja
</code></pre>

>> 1. **内连接**  
>> 默认是内连接，结果为俩表的交集，即可以省略inner关键字。<pre><code>SELECT * FROM TableA
INNER JOIN TableB
ON TableA.name = TableB.name
id  name       id   name
--  ----      --   ----
1   Pirate     2    Pirate
3   Ninja      4    Ninja
</code></pre>
>> 2. **外连接**  
>>> - **左外连接**  
>>> 结果为左表全部，右表符合条件。右表不符合条件的地方会置为null。<pre><code>SELECT * FROM TableA
LEFT OUTER JOIN TableB
ON TableA.name = TableB.name
id  name       id    name
--  ----       --    ----
1   Pirate     2     Pirate
2   Monkey     null  null
3   Ninja      4     Ninja
4   Spaghetti  null  null
</code></pre>
>>> - **右外连接**  
>>> 结果为右表全部，左表符合条件。左表不符合条件的地方会置为null。
>>> - **全外连接**  
>>> 结果和内连接对应，为俩表的并集(并非数学概念上的并集，这里为符合条件的并)。<pre><code>SELECT * FROM TableA
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
</code></pre>

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
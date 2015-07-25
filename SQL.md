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
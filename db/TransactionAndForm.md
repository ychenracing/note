# 事务的隔离级别
## 读现象
“读现象”是多个事务并发执行时，在读取数据方面可能碰到的状况。先了解它们有助于理解各隔离级别的含义。

### 脏读
脏读发生的前提是一个事务能读到其他事务中未提交的操作。
如果在读取到这样的数据后，那个事务进行了回滚，我们就相当于读到了数据库中不再存在的数据（也就是“脏数据”）。

### 不可重复读
还是将一条 SELECT 语句执行两次，某个特定的条目在这两次查询中返回的值不一样，就叫“不可重复读”。

```sql
SELECT id, name FROM test;    =>   (1,"n1"), (2, "n2"), (5, "n5")
SELECT id, name FROM test;    =>   (1, "n1"), (2, "David"), (5, "n5")
```

注意，返回的仍然是主键为 1,2,5 的数据，但 id=2 的那行数据的 name 变了。  
这种情况的原因是：在第二次 SELECT 前，其它事务对此条目进行了 UPDATE，并进行了提交。

### 幻读
**是指将同一条 SELECT 语句执行两次，得到了不同的“数据集”（就是说两次返回的不是同一批数据）。**

```sql
SELECT id FROM test;    =>  1,2,5
SELECT id FROM test;    =>  1,2,5,6 
```

出现这种请况一般是因为在第二次 SELECT 执行前，有其他事务进行了 INSERT 或 DELETE 操作，并进行了提交。

***这三种读现象是并列、互不相关的，例如在某个隔离等级中出现了“不可重复读”，并不意味着就一定也能出现“幻读”。***

## 隔离级别

SQL 标准中定义了4个隔离级别，一般来说，隔离级别越高，会出现的“读现象”就越少。  
但这只是一个规范。每种隔离级别在不同的数据库中有不同的特性和实现方式。  
这4个级别为：

### Read uncommitted（读未提交）
这是最宽松的级别。其他事务对数据进行的任意更改就算没提交，也会立刻反应到当前事务中。
所有读现象都可能出现在这个级别中。
因为太宽松了，这个级别很少被用到。

### Read committed（读已提交）
此级别中，其他事务对数据进行的更改只要一提交，就可以在当前事务中读取到。因此会出现“不可重复读”和“幻读”。

### Repeatable reads （可重复读）
比可串行化稍宽松一点的级别。
根据定义，此级别中不会出现“不可重复读”的现象，也就是其他事务对某行数据的更改无论提交没提交，都不会反应到当前事务中。
但是允许出现“幻读”，也就是其他事务中插入的新数据，允许出现在当前事务里。

### Serializable （串行化）
简单的说，此级别下运行的事务是完全隔离的，不会受到其他事务的干扰（因此不会出现任何“读现象”）。
其他事务中对数据进行的更新，在此事务中不可见（但可能导致此事务执行失败）。

从技术上来说，此级别下的事务必须以串行的方式被执行，或者至少是串行等价的，否则会以报错的形式结束并回滚。
“串行”也就是一个接一个的运行，这种情况下一个事务当然不会被其他事务干扰。
“串行等价”的意思就是：两个/多个事务就算同时运行（并行），得到的结果也和一个接一个的运行（串行）一样。所以对于这些事务，即使同时运行也没关系。

这是一个最理想的级别，我们可以认为在这个级别下不会因事务间的冲突而破坏数据一致性。
但相对的，性能也最低，所以不常用（也因此我实际并没有在此级别下运行过 SQL 语句，不清楚它到底有多强大）。

**MySQL 的默认事务级别是 `Repeatable read`**

Repeatable read 级别下，MySQL 使用了 Snapshot isolation。[什么是 Snapshot isolation？](http://en.wikipedia.org/wiki/Snapshot_isolation)  
因为这个特性，MySQL 和 PG 在这个级别下，都不会出现幻读。
但它们在选取快照的时机上有点差别：

假设有这样一条数据：`id=1, val=10`

```
A: BEGIN; 
B: BEGIN; 
A: UPDATE test SET val = 15 WHERE id = 1; COMMIT; 
B: SELECT val FROM test WHERE id = 1; # 在 MySQL 中返回 15
```

MySQL 会在第一次 SELECT 某个表时确定整个事务中要使用的快照，而 PG 会在事务一开始时就确定。

Repeatable read 级别下 MySQL 允许并发更新。

举个例子：

```
A: BEGIN;
B: BEGIN;
A: UPDATE test SET val=1 WHERE id = 1;
A: COMMIT;
B: UPDATE test SET val = 2 WHERE id = 1;
# Result In MySQL: Query OK, 1 row affected
```
在 MySQL 中执行 SELECT ... FOR UPDATE 总是能看到最新的数据（明明是 Repeatable Read 级别）

```
A: BEGIN;  B: BEGIN;
A: SELECT * FROM test;  B: SELECT * FROM test;
# 假设有这样一条数据： id=1, val = 5;
A: UPDATE test SET val = 10 WHERE id = 1;
A: COMMIT;
B: SELECT val FROM test WHERE id = 1 FOR UPDATE;
# Result in My: 10
# Result in PG: ERROR:  could not serialize access due to concurrent update
```

MySQL 下在 UPDATE 语句中执行自加、自减等操作，会把字段的最新提交上去的值作为基准值

```
A: BEGIN;  B: BEGIN;
# 假设有这样一条记录： id=1, val=5 
A: SELECT val FROM test WHERE id = 1;
B: SELECT val FROM test WHERE id = 1;   # 返回 5，这是正常的
A: UPDATE test SET val = 10 WHERE id = 1; COMMIT;
B: UPDATE test SET val = val + 1 WHERE id = 1; 
B: SELECT val FROM test WHERE id = 1;   # 返回 11，可见事务A的操作对此事务造成了影响
```

# 范式
## 第一范式
<font color="red">**字段不可分**</font>  
**定义**：如果关系R中所有属性的值域都是单纯域，那么关系模式R是第一范式的。  

那么符合第一模式的特点就有

1. 有主关键字
2. 主键不能为空
3. 主键不能重复
4. 字段不可以再分

例如：

|StudyNo   |   Name   |   Sex   |   Contact
|----------|----------|---------|----------
|20040901  |   john   |   Male  |Email:kkkk@ee.net,phone:222456|
|20040901  |   mary   |  famale |email:kkk@fff.net,phone:123455|

以上的表就不符合第一范式：主键重复(实际中数据库不允许重复的)，而且Contact字段可以再分

所以变更为正确的是

|  StudyNo  |  Name  |  Sex  |  Email  |  Phone  |
|-----------|--------|-------|---------|---------|
|  20040901 |  john  |Male |kkkk@ee.net|  222456 |
|  20040902 |  mary  |famale|kkk@fff.net| 123455 |

## 第二范式
<font color="red">**不能有（一个或多个）非主键列部分依赖于主键的情况**</font>  
**定义**：如果关系模式R是第一范式的，而且关系中每一个非主属性不部分依赖于主键，称R是第二范式的。

所以第二范式的主要任务就是：满足第一范式的前提下，消除部分函数依赖。

|StudyNo|Name|Sex|Email|Phone|ClassNo|ClassAddress|
|-------|----|---|-----|-----|-------|------------|
| 01 | john | Male |kkkk@ee.net|222456|200401|A楼2|
| 01 | mary |famale|kkk@fff.net|123455|200402|A楼3|

这个表完全满足于第一范式，主键由StudyNo和ClassNo组成，这样才能定位到指定行。但是，ClassAddress部分依赖于关键字( `ClassNo → ClassAddress` )，所以要变为两个表。

### 表一
|StudyNo|Name|Sex|Email|Phone|ClassNo|
|-------|----|---|-----|-----|-------|
|01|john|Male|kkkk@ee.net|222456|200401|     
|01|mary|famale|kkk@fff.net|123455|200402|

### 表二
|ClassNo|ClassAddress|
|-------|------------|
|200401|A楼2|
|200402|A楼3|

## 第三范式
<font color="red">**不能有（一个或多个）非主键列传递依赖于主键的情况**</font>  
**定义**：不存在非主属性对码的传递性依赖以及部分性依赖。

|StudyNo|Name|Sex|Email|bounsLevel|bouns|
|-------|----|---|-----|----------|-----|
|20040901|john|Male|kkkk@ee.net|优秀|$1000|
|20040902|mary|famale|kkk@fff.net|良|$600|

现在，主键是StudyNo，主键只有单个字段，显然符合第二范式，但是bounsLevel和bouns存在传递依赖。

更改为：

|StudyNo|Name|Sex|Email|bounsNo|
|-------|----|---|-----|--------|
|20040901|john|Male|kkkk@ee.net|1|
|20040902|mary|famale|kkk@fff.net|2|

|bounsNo|bounsLevel|bouns|
|-------|----------|-----|
|1|优秀|$1000|
|2|良|$600|

这里我比较喜欢用bounsNo作为主键，基于两个原因

1. 不要用字符作为主键。可能有人说：如果我的等级一开始就用数值就代替呢？

2. 但是如果等级名称更改了，不叫 1，2 ，3或优、良，这样就可以方便更改，所以我一般优先使用与业务无关的字段作为关键字。

一般满足前三个范式就可以避免数据冗余。

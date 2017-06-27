## MySQL
存储引擎（索引）：  
MyISAM（B+树），InnoDB（B+树）

### 组合索引

最左前缀原则：

- 按照索引的最左列开始查询。如果组合索引建立在第1、2、3列上，但是查询时只用到第2、3列，那么该查询仍要全表扫描，该组合索引未使用。
- 不能跳过索引中的列进行查询。
- 如果组合索引建立在第1、2、3列上，但是查询时只用到第1、3列，那么该查询只会利用到第1列的索引，然后对第1列索引查出来的记录进行全部扫描。
- 如果查询时某个列使用了范围查询，则其右边的列都无法使用索引进行查询优化。

order by和group by也遵循最左前缀原则。

如，

```sql
alter table city add index city_index(vc_Name, vc_City, i_Age)
```

建立这样的组合索引，其实是相当于分别建立了

```sql
vc_Name,vc_City,i_Age  
vc_Name,vc_City  
vc_Name 
```

例，

```sql
CREATE TABLE `test_table` (
  `activity_id` bigint(20) NOT NULL COMMENT '优惠活动id',
  `collected` bigint(20) NOT NULL DEFAULT '0' COMMENT '领取量',
  `used` bigint(20) NOT NULL DEFAULT '0' COMMENT '使用量',
  `pack_num` bigint(20) NOT NULL DEFAULT '0' COMMENT '订单数',
  `order_num` bigint(20) NOT NULL DEFAULT '0' COMMENT '子订单数',
  `fee` bigint(20) NOT NULL DEFAULT '0' COMMENT '优惠金额',
  `order_fee` bigint(20) NOT NULL DEFAULT '0' COMMENT '订单金额',
  `day` date NOT NULL DEFAULT '0000-00-00' COMMENT '日期',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx` (`activity_id`,`order_fee`,`day`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

下面的查询语句，打钩的表示该句用到了组合索引

```sql
explain select * from test_table where activity_id = 1 and order_fee = 0 and day = "0000-00-00"; √
explain select * from test_table where activity_id = 1 and order_fee = 0; √
explain select * from test_table where activity_id = 1; √
explain select * from test_table where order_fee = 1;
explain select activity_id, order_fee, day from test_table where day = "2016-10-20"; √
explain select activity_id, order_fee, day from test_table where order_fee = 1; √
explain select order_fee, day, activity_id from mall_coupon_activity_day_stat where order_fee = 1; √
explain select day from test_table where order_fee = 1; √
explain select activity_id, order_fee, create_time from test_table where day = "2016-10-20";
explain select activity_id, order_fee, create_time from test_table where activity_id = 1; √
explain select activity_id, order_fee, create_time from test_table where order_fee = 1;
explain select activity_id, order_fee, create_time from test_table where fee = 1;
explain select activity_id, order_fee from test_table where fee = 1 and activity_id = 1; √
```

#### 组合索引总结

1. 如果`select`中的字段全部是组合索引的字段（不在乎顺序），那么，只要`where`中的字段全都是组合索引的字段（不在乎顺序、个数），那么该组合索引就会在该`select`中用到。
2. 如果`select`中存在组合索引中没有的字段，那么，只要`where`中所有字段组合起来（可以是任意顺序）符合组合索引的最左前缀原则，那么该组合索引就会在该`select`中用到。
3. 其他情况该组合索引不会被用到。

## B+树
在数据库索引的应用中，B+树按照下列方式进行组织：

①叶结点的组织方式：

- B+树的查找键是数据文件的主键，且索引是稠密的。也就是说，叶结点中为数据文件的第一个记录设有一个键、指针对，该数据文件可以按主键排序，也可以不按主键排序；数据文件按主键排序，且B+树是稀疏索引，在叶结点中为数据文件的每一个块设有一个键、指针对；数据文件不按键属性排序，且该属性是B+树的查找键，叶结点中为数据文件里出现的每个属性K设有一个键、指针对，其中指针执行排序键值为K的记录中的第一个。

②非叶结点的组织方式：

- B+树中的非叶结点形成了叶结点上的一个**多级稀疏索引**。每个非叶结点中至少有 ceil(m/2) 个指针，至多有m个指针。

### B+树索引的插入和删除
①在向数据库中插入新的数据时，同时也需要向数据库索引中插入相应的索引键值，则需要向B+树中插入新的键值。即B-树的插入算法。  
②当从数据库中删除数据时，同时也需要从数据库索引中删除相应的索引键值，则需要从B+树中删除该键值。即B-树的删除算法。

### 为什么使用B-Tree（B+Tree）
二叉查找树进化品种的红黑树等数据结构也可以用来实现索引，但是文件系统及数据库系统普遍采用B-/+Tree作为索引结构。

一般来说，索引本身也很大，不可能全部存储在内存中，因此索引往往以索引文件的形式存储的磁盘上。这样的话，索引查找过程中就要产生磁盘I/O消耗，相对于内存存取，I/O存取的消耗要高几个数量级，所以评价一个数据结构作为索引的优劣最重要的指标就是在查找过程中磁盘I/O操作次数的渐进复杂度。换句话说，**索引的结构组织要尽量减少查找过程中磁盘I/O的存取次数**。为什么使用B-/+Tree，还跟磁盘存取原理有关。

### 局部性原理与磁盘预读
由于存储介质的特性，磁盘本身存取就比主存慢很多，再加上机械运动耗费，磁盘的存取速度往往是主存的几百分之一，因此为了提高效率，要尽量减少磁盘I/O。为了达到这个目的，磁盘往往不是严格按需读取，而是**每次都会预读**，即使只需要一个字节，磁盘也会从这个位置开始，顺序向后读取一定长度的数据放入内存。这样做的理论依据是计算机科学中著名的局部性原理：

- 当一个数据被用到时，其附近的数据也通常会马上被使用。
- 程序运行期间所需要的数据通常比较集中。

由于磁盘顺序读取的效率很高（不需要寻道时间，只需很少的旋转时间），因此对于具有局部性的程序来说，预读可以提高I/O效率。

预读的长度一般为页（page）的整倍数。页是计算机管理存储器的逻辑块，硬件及操作系统往往将主存和磁盘存储区分割为连续的大小相等的块，每个存储块称为一页（在许多操作系统中，页得大小通常为4k），主存和磁盘以页为单位交换数据。当程序要读取的数据不在主存中时，会触发一个缺页异常，此时系统会向磁盘发出读盘信号，磁盘会找到数据的起始位置并向后连续读取一页或几页载入内存中，然后异常返回，程序继续运行。

数据库系统巧妙利用了磁盘预读原理，将一个节点的大小设为等于一个页，这样每个节点只需要一次I/O就可以完全载入。为了达到这个目的，在实际实现B-Tree还需要使用如下技巧：

每次新建节点时，直接申请一个页的空间，这样就保证一个节点物理上也存储在一个页里，加之计算机存储分配都是按页对齐的，就实现了一个node只需一次I/O。

B-Tree中一次检索最多需要h-1次I/O（根节点常驻内存），渐进复杂度为O(h)=O(logmN)。一般实际应用中，m是非常大的数字，通常超过100，因此h非常小（通常不超过3）。

综上所述，用B-Tree作为索引结构效率是非常高的。

而红黑树这种结构，h明显要深的多。由于逻辑上很近的节点（父子）物理上可能很远，无法利用局部性，所以红黑树的I/O渐进复杂度也为O（h），效率明显比B-Tree差很多。


### MySQL的B-Tree索引（技术上说B+Tree）
在MySQL中，主要有四种类型的索引，分别为： B-Tree 索引， Hash 索引， Fulltext 索引和 R-Tree 索引。我们主要分析B-Tree 索引。

B-Tree 索引是 MySQL 数据库中使用最为频繁的索引类型，除了 Archive 存储引擎之外的其他所有的存储引擎都支持 B-Tree 索引。Archive 引擎直到 MySQL 5.1 才支持索引，而且只支持索引单个 AUTO_INCREMENT 列。

不仅仅在 MySQL 中是如此，实际上在其他的很多数据库管理系统中B-Tree 索引也同样是作为最主要的索引类型，这主要是因为 B-Tree 索引的存储结构在数据库的数据检索中有非常优异的表现。

一般来说， MySQL 中的 B-Tree 索引的物理文件大多都是以 Balance Tree 的结构来存储的，也就是所有实际需要的数据都存放于 Tree 的 Leaf Node(叶子节点) ，而且到任何一个 Leaf Node 的最短路径的长度都是完全相同的，所以我们大家都称之为 B-Tree 索引。当然，可能各种数据库（或 MySQL 的各种存储引擎）在存放自己的 B-Tree 索引的时候会对存储结构稍作改造。如 Innodb 存储引擎的 B-Tree 索引实际使用的存储结构实际上是 B+Tree，也就是在 B-Tree 数据结构的基础上做了很小的改造，在每一个Leaf Node 上面出了存放索引键的相关信息之外，还存储了指向与该 Leaf Node 相邻的后一个 LeafNode 的指针信息（增加了顺序访问指针），这主要是为了加快检索多个相邻 Leaf Node 的效率考虑。

## MyISAM索引实现：
### 主键索引
MyISAM引擎使用B+Tree作为索引结构，叶节点的data域存放的是数据记录的地址。下图是MyISAM主键索引的原理图：  
![](img/localFileServerNode.png)  
这里设表一共有三列，假设我们以Col1为主键，图myisam1是一个MyISAM表的主索引（Primary key）示意。可以看出MyISAM的索引文件仅仅保存数据记录的地址。

### 辅助索引（Secondary key）
**在MyISAM中，主键索引和辅助索引（Secondary key）在结构上没有任何区别，只是主索引要求key是唯一的，而辅助索引的key可以重复**。如果我们在Col2上建立一个辅助索引，则此索引的结构如下图所示：  
![](img/1343757949_9784.png)  
同样也是一颗B+Tree，data域保存数据记录的地址。因此，MyISAM中索引检索的算法为首先按照B+Tree搜索算法搜索索引，如果指定的Key存在，则取出其data域的值，然后以data域的值为地址，读取相应数据记录。  

MyISAM的索引方式也叫做“非聚集”的，之所以这么称呼是为了与InnoDB的聚集索引区分。

## InnoDB索引实现
然而InnoDB也使用B+Tree作为索引结构，但具体实现方式却与MyISAM截然不同。

### 主键索引：
**MyISAM索引文件和数据文件是分离的，索引文件仅保存数据记录的地址。而在InnoDB中，表数据文件本身就是按B+Tree组织的一个索引结构，这棵树的叶节点data域保存了完整的数据记录**。这个索引的key是数据表的主键，因此InnoDB表数据文件本身就是主索引。  
![](img/1343758042_8526.png)  
上图是InnoDB主索引（同时也是数据文件）的示意图，可以看到叶节点包含了完整的数据记录。这种索引叫做<font color="red">聚集索引</font>。因为InnoDB的**数据文件本身要按主键聚集**，所以InnoDB要求表必须有主键（MyISAM可以没有），如果没有显式指定，则MySQL系统会自动选择一个可以唯一标识数据记录的列作为主键，如果不存在这种列，则MySQL自动为InnoDB表生成一个隐含字段作为主键，这个字段长度为6个字节，类型为长整形。

### InnoDB的辅助索引
InnoDB的所有辅助索引都引用主键作为data域。例如，下图为定义在Col3上的一个辅助索引：  
![](img/1343758434_9462.png)  

InnoDB 表是基于**聚簇索引**建立的。因此InnoDB 的索引能提供一种非常快速的主键查找性能。不过，它的辅助索引（Secondary Index， 也就是非主键索引）也会包含主键列，所以，如果主键定义的比较大，其他索引也将很大。如果想在表上定义 、很多索引，则争取尽量把主键定义得小一些。InnoDB 不会压缩索引。

文字符的ASCII码作为比较准则。聚集索引这种实现方式使得按主键的搜索十分高效，但是辅助索引搜索需要检索两遍索引：首先检索辅助索引获得主键，然后用主键到主索引中检索获得记录。

不同存储引擎的索引实现方式对于正确使用和优化索引都非常有帮助，例如知道了InnoDB的索引实现后，就很容易明白为什么不建议使用过长的字段作为主键，因为所有辅助索引都引用主索引，过长的主索引会令辅助索引变得过大。再例如，用非单调的字段作为主键在InnoDB中不是个好主意，因为InnoDB数据文件本身是一颗B+Tree，非单调的主键会造成在插入新记录时数据文件为了维持B+Tree的特性而频繁的分裂调整，十分低效，而使用自增字段作为主键则是一个很好的选择。

### InnoDB索引和MyISAM索引的区别：
- 一是主索引的区别，InnoDB的数据文件本身就是索引文件。而MyISAM的索引和数据是分开的。
- 二是辅助索引的区别：InnoDB的辅助索引data域存储相应记录主键的值而不是地址。而MyISAM的辅助索引和主键索引没有多大区别。

## Reference
[1][经典好文：B-树和B+树的应用：数据搜索和数据库索引](http://blog.csdn.net/hguisu/article/details/7786014)

[2][记一次MySql单列索引和联合索引的使用区别](https://my.oschina.net/857359351/blog/658668)

[3][MySQL单列索引和组合索引(联合索引)的区别详解](http://www.phpsong.com/586.html)


#Redis#
高性能key-value数据库，不仅支持简单的key-value存储，还支持其他一系列的数据存储结构如strings、hashs、lists、sets、sorted sets等，并在这些数据结构类型上定义了一套强大的API。

- 更丰富的数据类型，较于传统关系型数据库的更好的读写吞吐能力，更高的并发数。
- 可以很轻易的完成其他key-value很难完成的任务如排序、去重、取topN、访问计数器、队列系统等。
- 将服务器设置为cache-only可以提供该性能的缓存服务。

##Jedis:redis的java客户端实现##

```java
Jedis redis = new Jedis("127.0.0.1", 6379);

// 支持strings
redis.set("name", "y"); // 设置一条记录name-ychen
redis.setex("age", 100 * 365 * 12 * 31 * 24 * 60 * 60, "100"); // 设置age-100的有效时间为100年
redis.mset("merried", "no", "career", "student"); // 设置多个[key]-[value]
redis.append("name", "chen"); //向name中追加chen
String name = redis.get("name"); //获取name的值
List<String> list = redis.mget("merried", "career"); // 获取多个key的value

// 支持hashs
redis.hset("person-ychen", "name", "ychen");
redis.hset("person-ychen", "age", "100");
redis.hset("person-ychen", "career", "student");

Map<String, String> personMap = new HashMap<String, String>();
personMap.put("name", "li");
personMap.put("age", "100");
personMap.put("career", "student");
redis.hmset("personal-li", personMap);

List<String> hlist = redis.hmget("person-li", "name", "age", "career");

Map<String, String> liMap = redis.hgetAll("person-li");

// 支持lists
redis.lpush("persons", "left No.1");
redis.lpush("persons", "left No.2");
redis.rpush("persons", "right No.1");
redis.rpush("persons", "right No.2");
redis.lpop("persons");

List<String> personList = redis.lrange("persons", 1, 3);
Long personListSize = redis.llen("persons");

// 支持sets
redis.sadd("person-set", "chen");
redis.sadd("person-set", "li");
redis.sadd("person-set", "qing");
redis.sadd("person-set", "min");
redis.sadd("person-set", "min");
redis.srem("person-set", "qing");
Set<String> set = redis.smembers("person-set");

// 支持sorted sets
redis.zadd("person-sorted-set", 1, "5th");
redis.zadd("person-sorted-set", 2, "4th");
redis.zadd("person-sorted-set", 3, "3th");
redis.zadd("person-sorted-set", 4, "2th");
redis.zadd("person-sorted-set", 5, "1th");

Set<String> sortset = redis.zrange("person-sorted-set", 2, 4);

System.out.println(sortset.toString());
```

##Redis的hashs##
![](img/image1.jpg)  
首先Redis内部使用一个redisObject对象来表示所有的key和value,redisObject最主要的信息如上图所示：type代表一个value对象具体是何种数据类型，encoding是不同数据类型在redis内部的存储方式，比如：type=string代表value存储的是一个普通字符串，那么对应的encoding可以是raw或者是int,如果是int则代表实际redis内部是按数值型类存储和表示这个字符串的，当然前提是这个字符串本身可以用数值表示，比如:"123" "456"这样的字符串。

这里需要特殊说明一下vm字段，只有打开了Redis的虚拟内存功能，此字段才会真正的分配内存，该功能默认是关闭状态的，该功能会在后面具体描述。通过上图我们可以发现Redis使用redisObject来表示所有的key/value数据是比较浪费内存的，当然这些内存管理成本的付出主要也是为了给Redis不同数据类型提供一个统一的管理接口，实际作者也提供了多种方法帮助我们尽量节省内存使用，我们随后会具体讨论。

Redis Hash对应Value内部实际就是一个HashMap，实际这里会有2种不同实现，这个Hash的成员比较少时Redis为了节省内存会采用类似一维数组的方式来紧凑存储（zipmap），而不会采用真正的HashMap结构，对应的value redisObject的encoding为zipmap,当成员数量增大时会自动转成真正的HashMap,此时encoding为ht。
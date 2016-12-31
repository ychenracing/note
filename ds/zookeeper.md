#ZooKeeper#
- 持久和非持久节点，使得几乎可以实时感知到后端服务器状态。
- 可以集群复制，Zookeeper Atomic Broadcast协议，使得服务配置信息保持一致。
- 容错特性和leader选举，使得可以很方便的扩容。

##Zab协议##
1. leader election
2. Atomic Broadcast

集群选举出一个leader，其他成为follower，所有写操作都传送给leader，并通过broadcast将所有更新告诉follower。

ZooKeeper实现了一个层次命名空间的数据模型，看起来像是一个小型的，精密的文件系统。把集群中的一个节点表示成znode，znode有4种节点类型，4种节点状态变化。

```java
String url = "127.0.0.1";
ZooKeeper zooKeeper = new ZooKeeper(url, 600, null);//    最后一个参数watcher为null，表示不注册watcher  
zooKeeper.create("/Users/racing", "racing data".getBytes(), Ids.OPEN_ACL_UNSAFE,
    CreateMode.PERSISTENT);

zooKeeper.delete("/Users/racing", -1);

zooKeeper.setData("/Users/racing", "new racing data".getBytes(), -1);

Stat stat = new Stat();
byte[] data = zooKeeper.getData("/Users/racing", false, stat);

zooKeeper.create("/Users/racing/Downloads", "racing data".getBytes(), Ids.OPEN_ACL_UNSAFE,
    CreateMode.PERSISTENT);

Stat state = zooKeeper.exists("/Users/racing/Documents", false);
if (state == null) {
    System.out.println("节点不存在");
}
```

```java
private class ZKWatcher implements Watcher {

    @Override
    public void process(WatchedEvent event) {
        if (event.getType() == EventType.NodeDeleted) {
            System.out.println("节点已删除，可以做一些删除后处理工作！");
        }
        if (event.getType() == EventType.NodeCreated) {
            System.out.println("节点创建！");
        }
        if (event.getType() == EventType.NodeDataChanged) {
            System.out.println("节点数据变更！");
        }
        if (event.getType() == EventType.NodeChildrenChanged) {
            System.out.println("节点的子节点有变化！");
        }
    }
}
```

每次watcher处理之后，该注册的watcher失效，需要重新注册该节点的watcher。

使用ZooKeeper第三方工具包zkclient.jar可以解决重新注册的麻烦。zkclient在一个watcher生效的时候，会自动重新注册一个相同的watcher。其把ZooKeeper的四种节点状态的变化类型封装成了三种：子节点的变化，节点连接和状态变化，节点数据变化。在ZooKeeper中注册watcher是实现Watcher接口，在zkclient中是向zookeeper的一个节点注册IZkStateListener、IZkChildListener、IZkDataListener的实现。

zkclient还提供了ZkSerializer接口，简化了znode的数据存储。

```java
ZkClient zkClient = new ZkClient("127.0.0.1");
zkClient.create("/root", "root date", CreateMode.PERSISTENT);

List<String> children = zkClient.getChildren("/root");

int count = zkClient.countChildren("/root")
```

zkclient注册watcher。生效之后会自动注册相同的watcher。

```java
zkClient.subscribeChildChanges("/root", new IZkChildListener() {

    @Override
    public void handleChildChange(String parentPath, List<String> currentChildren)
                                                                                  throws Exception {
        System.out.println(currentChildren.toString());
    }
});

zkClient.subscribeDataChanges("/root", new IZkDataListener() {

    @Override
    public void handleDataDeleted(String dataPath) throws Exception {
        System.out.println("date deleted: " + dataPath);
    }

    @Override
    public void handleDataChange(String dataPath, Object data) throws Exception {

    }
});
    
zkClient.subscribeStateChanges(new IZkStateListener() {
    
    @Override
    public void handleStateChanged(KeeperState arg0) throws Exception {
    }
    
    @Override
    public void handleNewSession() throws Exception {
    }
});
```

当发生session expire异常的时候，进行重连，原来所有的session和EPHEMERAL都失效，可以在handleNewSession进行容错处理。

![configurer tree](img/configurerTree.png "configurer tree")

##集群Master单点故障问题##
- ZooKeeper的leader选举。
- Dual-Master双机互为备份，实现故障切换。如Mysql、Nginx等。

## 分布式锁##

### CAP理论###

任何分布式系统都无法同时满足一致性（Consistency）、可用性（Availability）和分区容错性（Partition tolerance），最多只能同时满足其中两项。

一般来说，我们牺牲一致性，保证数据的最终一致性。

### 分布式锁实现方式###

1. 基于数据库实现
2. 基于缓存实现
3. 基于Zookeeper实现

#### 基于数据库实现####

1. 基于数据库中某张表的一条记录。要获取锁时，插入一条记录，释放锁时，删除该记录。专门建立一个数据库，用来存放获取分布式锁的表。比如，新建一张`shop`表:

```sql
CREATE TABLE `shop` (
  `id` bigint(20) NOT NULL COMMENT '店铺id，主键',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY(`id`)
)
```

要锁住某个店铺时，执行：

```sql
INSERT INTO `shop` VALUES (132756382, now());
```

释放某个店铺的锁时，执行：

```sql
DELETE FROM `shop` WHERE ID = 132756382
```

// 单点故障问题

2. 基于数据库中的排它锁（悲观锁）。

使用悲观锁，在查询数据时就把当前数据锁定，直到修改完毕后再解锁。

InnoDB引擎中，仍然使用上面的表，每个店铺都在`shop`表中先插入一条记录。

```java
public boolean lock() {
    connection.setAutoCommit(false);
    while (true) {
        try {
            // select ... for update根据主键查询到了数据时，返回集不为空，此时已经锁住了该条记录。
            result = update("select * from shop where id=132756382 for update;");
            // 其他线程执行该select ... for update时，则会被阻塞住，而且可能会因为获取悲观锁而超时报错。
            if (result != null) {
                return true;
            }
        } catch (Exception e) {
        }
        sleep(1000);
    }
    return false;
}
```

执行了`select ... for update`之后，id为132756382的那条店铺记录就被锁定了。

释放锁时，执行：

```java
connection.commit();
```

// 单点故障问题

#### 基于缓存实现####

缓存一般有缓存集群。也可能会使用一致性哈希来解决缓存数据冗余和缓存数据不一致的问题。

redis的setnx（set if not exists），memcached的add函数（多线程add时，只有第一个add会成功，返回true，其他会返回false，多线程set时，都会成功，返回true）。

##### Redis SETNX和GETSET#####

`SETNX key value`当且仅当key不存在时，把key对应的值设为value，返回1；否则返回0。

`GETSET key value`把key对应的值设为value，返回key的旧值。

对店铺加锁时，执行：

```shell
SETNX shop:132756382 [当前时间]
```

释放锁，执行：

```shell
DEL shop:132756382
```

// 死锁问题。如果获取到锁的进程异常终止导致没有释放锁，则其他进程获取不到锁。

加入超时机制避免死锁，每个进程要获取锁时先`GET shop:132756382`，协商锁的超时时间，如果上一进程锁超时，则获取锁的进程执行：

```SHELL
DEL shop:132756382
SETNX shop:132756382 [当前时间]
```

// 多个进程获取到锁的问题，进程1获取到锁，崩溃之后。进程2和进程3获取到进程1的锁的时间戳，超时之后，进程2和进程3分别实行：

```shell
DEL shop:132756382
SETNX shop:132756382 [进程2的当前时间]
DEL shop:132756382 【此处进程3删除了进程2加的锁】
SETNX shop:132756382 [进程3的当前时间]【此处进程3也获取到了锁】
```

采用`GETSET shop:132756382 [当前时间]`避免多进程获取到锁。进程1获取到锁，崩溃之后。进程2和进程3执行`GET`获取到进程1的锁的时间戳，超时之后，进程2和进程3分别执行`GETSET`，对比`GET`和`GETSET`的返回值，一样则表示获取到锁，否则，则表示其他进程获取到锁。

#### 基于Zookeeper实现####

Zookeeper本身配置为一个集群，客户端连接不同的Zookeeper服务器，但是得到的视图是一样的，这是Zookeeper自身保证的。

通过实现`IZkChildListener`的`handleChildChange`方法来注册子节点变化。

想要获取锁时，在Zookeeper下某节点下（比如要获取店铺锁，就在店铺节点下）创建一个临时有序的节点`createEphemeralSequential`。然后获取节点下（店铺节点）的所有子节点，如果子节点中，自己刚创建的临时有序节点是最小的，则表示自己获取到锁（此时可以设置一个缓存位，表示锁已被获取），否则，如果自己刚创建的临时有序节点不是最小的，则把自己挂起（wait释放CPU资源释放锁），被唤醒时，在检测缓存位和节点下的最小有序节点是否存在并且是不是自己。释放锁时，删除自己的临时有序节点。在`handleChildChange`子节点变化中，唤醒所有被缓存位阻塞的获取所的线程。




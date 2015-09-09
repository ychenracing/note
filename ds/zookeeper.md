#ZooKeeper#
- 持久和非持久节点，使得几乎可以实时感知到后端服务器状态。
- 可以集群复制，Zookeeper Atomic Broadcast协议，使得服务配置信息保持一致。
- 容错特性和leader选举，使得可以很方便的扩容。

##Zab协议##
1. leader election
2. Atomic Broadcast

集群选举出一个leader，其他成为follower，所有写操作都传送给leader，并通过broadcast将所有更新告诉follower。
##分布式通信##

###通信模型###
- RPC
- 消息
- 流

###通信模式###
- request/response
- oneway
- callback
- future
- pub/sub
- multicast

##ActiveMQ&JMS##
- p2p模型，基于消息队列。
- 发布/订阅模型，基于内容节点(主题)。

###p2p###
```java
public static void activemqQueueSender() throws JMSException {
    ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(
        ActiveMQConnection.DEFAULT_USER, ActiveMQConnection.DEFAULT_PASSWORD,
        "tcp://192.168.0.106:4621");

    Connection connection = connectionFactory.createConnection();
    connection.start();

    // 第一个参数，是否采用事务消息。如果是事务，消息的提交自动由commit处理。
    Session session = connection.createSession(Boolean.TRUE, Session.AUTO_ACKNOWLEDGE);
    Destination destination = session.createQueue("MessageQueue");

    MessageProducer messageProducer = session.createProducer(destination);
    messageProducer.setDeliveryMode(DeliveryMode.NON_PERSISTENT);

    ObjectMessage message = session.createObjectMessage("hello everyone!");
    messageProducer.send(message);
    session.commit();
}

public static void activemqQueueReceiver() throws JMSException {
    ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(
        ActiveMQConnection.DEFAULT_USER, ActiveMQConnection.DEFAULT_PASSWORD,
        "tcp://192.168.0.106:4621");

    Connection connection = connectionFactory.createConnection();
    connection.start();

    // 第一个参数，是否采用事务消息。如果是事务，消息的提交自动由commit处理。
    Session session = connection.createSession(Boolean.TRUE, Session.AUTO_ACKNOWLEDGE);
    Destination destination = session.createQueue("MessageQueue");

    MessageConsumer messageConsumer = session.createConsumer(destination);

    while (true) {
        ObjectMessage message = (ObjectMessage) messageConsumer.receive(10000);// 超时时间
        if (message != null) {
            String messageContent = (String) message.getObject();
            System.out.println(messageContent);
        } else {
            break;
        }
    }
}

```

###pub/sub###
```java
public static void activemqTopicSender() throws JMSException {
    ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(
        ActiveMQConnection.DEFAULT_USER, ActiveMQConnection.DEFAULT_PASSWORD,
        "tcp://192.168.0.106:4621");

    Connection connection = connectionFactory.createConnection();
    connection.start();

    // 第一个参数，是否采用事务消息。如果是事务，消息的提交自动由commit处理。
    Session session = connection.createSession(Boolean.FALSE, Session.AUTO_ACKNOWLEDGE);

    Topic topic = session.createTopic("MessageTopic");

    MessageProducer messageProducer = session.createProducer(topic);
    messageProducer.setDeliveryMode(DeliveryMode.NON_PERSISTENT);

    TextMessage message = session.createTextMessage("hello everyone!");
    messageProducer.send(message);
}

public static void activemqTopicReceiver() throws JMSException {
    ConnectionFactory connectionFactory = new ActiveMQConnectionFactory(
        ActiveMQConnection.DEFAULT_USER, ActiveMQConnection.DEFAULT_PASSWORD,
        "tcp://192.168.0.106:4621");

    Connection connection = connectionFactory.createConnection();
    connection.start();

    // 第一个参数，是否采用事务消息。如果是事务，消息的提交自动由commit处理。
    Session session = connection.createSession(Boolean.FALSE, Session.AUTO_ACKNOWLEDGE);
    Topic topic = session.createTopic("MessageTopic");

    MessageConsumer messageConsumer = session.createConsumer(topic);
    // 需要向该topic注册listener，才能够接收该topic的消息。
    messageConsumer.setMessageListener(new MessageListener() {

        @Override
        public void onMessage(Message message) {
            TextMessage tm = (TextMessage) message;
            try {
                System.out.println(tm.getText());
            } catch (JMSException ex) {
            }
        }
    });
}
```

##ActiveMQ集群##
与分布式缓存集群，分布式服务集群和分布式存储集群不一样，ActiveMQ消息服务集群一般只有一个服务器（Master）在对外提供服务，其他是standby的。其基于Master-slave架构。有两种架构模式：

###基于共享文件系统的Master-Slave架构###
Master启动时，会获得共享文件系统的排它锁，其他slave则stand by。Master宕机或异常时，会自动释放锁，有一个slave会争夺到排它锁，成为新的Master。旧的Master恢复之后重新链接共享文件系统时，变成了slave。
###基于共享数据库的Master-Slave架构###
Master启动时，会获得数据库某个表的排它锁，其他slave则stand by。Master宕机或异常时，会自动释放锁，有一个slave会争夺到排它锁，成为新的Master。旧的Master恢复之后重新链接共享文件系统时，变成了slave。

如果想让Master-Slave切换而客户无需重启和更改配置时，需要在ActiveMQ的客户端连接的配置中使用failover:  

```
failover:(tcp://master:61616, tcp:slave1:61616, tcp://slave2:61616)
```

假设Master失效，客户端能够自动的连接到Slave1和Slave2两台当中成功获取排它锁的新Master。

##JMS提升并发能力##
- 提升硬件。
- 更改配置如io改为nio。
- 拆分broker：将不相关的queue和topic拆出来放到多个broker中。
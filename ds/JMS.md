##分布式通信##

###通信模型###
- RPC
- 消息
- 流

###通信模式###
- request/response: 客户端发起请求一直阻塞到服务端返回请求为止。
- oneway: 客户端调用完继续执行，不管接收端是否成功。
- callback: 客户端发送一个RPC请求给服务器，服务端处理后再发送一个消息给消息发送端提供的callback端点，此类情况非常合适以下场景：A组件发送RPC请求给B，B处理完成后，需要通知A组件做后续处理。
- future: 客户端发送完请求后，继续做自己的事情，返回一个包含消息结果的Future对象。客户端需要使用返回结果时，使用Future对象的.get(),如果此时没有结果返回的话，会一直阻塞到有结果返回为止。
- pub/sub: 生产者把消息发布到broker上，消费者在broker上订阅感兴趣的消息。broker一般由中间件实现，如kafka。
- multicast: 

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


##Kafka 分布式消息系统－发布订阅模式##
我们将消息的发布（publish）暂时称作producer，将消息的订阅（subscribe）表述为consumer，将中间的存储阵列称作broker，这样我们就可以大致描绘出这样一个场面：

![pub/sub](http://img.blog.csdn.net/20131221001202421?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvaXRsZW9jaGVu/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

生产者将数据生产出来，丢给broker进行存储，消费者需要消费数据了，就从broker中去拿出数据来，然后完成一系列对数据的处理。
乍一看这也太简单了，不是说了它是分布式么，难道把producer、broker和consumer放在三台不同的机器上就算是分布式了么。我们看kafka官方给出的图：

![kafka pub/sub](http://img.blog.csdn.net/20131221001230046?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvaXRsZW9jaGVu/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

整个系统运行的顺序：

1. 启动zookeeper的server
2. 启动kafka的server（broker），注册在zookeeper上
3. Producer如果生产了数据，会先通过zookeeper找到broker，然后将数据存放进broker
4. Consumer如果要消费数据，会先通过zookeeper找对应的broker，然后消费。

##Reference##
1. [Kafka分布式消息发布和订阅系统简介](http://blog.csdn.net/itleochen/article/details/17457209)

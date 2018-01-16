## IO复用

```cpp
// 非阻塞忙轮询
while true
{
    for i in stream[]
    {
        if i has data
            read until unavailable
    }
}
```

<font color="red">为了避免CPU空转！！！</font>

```cpp
// select poll I/O多路复用

// 计算机所有的问题都可以增加一个中间层来解决，同样，为了避免这里cpu的空转，我们不让这个线程亲自去检查流中是否有事件。
// 而是引进了一个代理(一开始是select,后来是poll)，这个代理很牛，它可以同时观察许多流的I/O事件，如果没有事件，代理就阻塞，线程就不会挨个挨个去轮询了。
// 伪代码如下：
while true
{
    // 阻塞，不释放锁，释放CPU
    select(streams[]) //这一步阻塞在这里，直到有一个流有I/O事件时，才往下执行
    for i in streams[]
    {
        if i has data
            read until unavailable
    }
}
```

```cpp
// epoll I/O多路复用

// epoll可以理解为event poll，不同于忙轮询和无差别轮询，epoll会把哪个流发生了怎样的I/O事件通知我们。
// 所以我们说epoll实际上是事件驱动（每个事件关联上fd）的，此时我们对这些流的操作都是有意义的。
//（复杂度降低到了O(1)）伪代码如下：
while true
{
    active_stream[] = epoll_wait(epollfd)
    for i in active_stream[]
    {
        read or write till
    }
}
```

IO多路复用是指内核一旦发现进程指定的一个或者多个IO条件准备读取，它就通知该进程。IO多路复用适用如下场合：

1. 当客户处理多个描述字时（一般是交互式输入和网络套接口），必须使用I/O复用。
2. 当一个客户同时处理多个套接口时，而这种情况是可能的，但很少出现。
3. 如果一个TCP服务器既要处理监听套接口，又要处理已连接套接口，一般也要用到I/O复用。
4. 如果一个服务器即要处理TCP，又要处理UDP，一般要使用I/O复用。
5. 如果一个服务器要处理多个服务或多个协议，一般要使用I/O复用。

　　与多进程和多线程技术相比，I/O多路复用技术的最大优势是系统开销小，系统不必创建进程/线程，也不必维护这些进程/线程，从而大大减小了系统的开销。

## select
该函数准许进程指示内核等待多个事件中的任何一个发送，并只在有一个或多个事件发生或经历一段指定的时间后才唤醒。关键在于需要<font color="red">轮询</font>。

select的几大缺点：

1. 每次调用select，都需要把fd集合从用户态拷贝到内核态，这个开销在fd很多时会很大。
2. 同时每次调用select都需要在内核遍历传递进来的所有fd，这个开销在fd很多时也很大。
3. select支持的文件描述符数量太小了，默认是1024。

## poll
poll的机制与select类似，与select在本质上没有多大差别，管理多个描述符也是进行轮询，根据描述符的状态进行处理，但是poll没有最大文件描述符数量的限制，原因是它是基于链表来存储的。poll和select同样存在一个缺点就是，<font color="red">包含大量文件描述符的数组被整体复制于用户态和内核的地址空间之间，而不论这些文件描述符是否就绪，它的开销随着文件描述符数量的增加而线性增大</font>。

poll的实现和select非常相似，只是描述fd集合的方式不同，poll使用pollfd结构而不是select的fd_set结构，其他的都差不多。

## epoll
epoll是在2.6内核中提出的，是之前的select和poll的增强版本。相对于select和poll来说，epoll更加灵活，没有描述符限制。<font color="red">epoll使用一个文件描述符管理多个描述符，将用户关系的文件描述符的事件存放到内核的一个事件表中，这样在用户空间和内核空间的copy只需一次</font>。

epoll支持水平触发和边缘触发，最大的特点在于边缘触发，它只告诉进程哪些fd刚刚变为就绪态，并且只会通知一次。

## 综合
- select，poll实现需要自己不断轮询所有fd集合，直到设备就绪，期间可能要睡眠和唤醒多次交替。而epoll其实也需要调用 epoll\_wait不断轮询就绪链表，期间也可能多次睡眠和唤醒交替，但是它是设备就绪时，调用回调函数，把就绪fd放入就绪链表中，并唤醒在 epoll\_wait中进入睡眠的进程。虽然都要睡眠和交替，但是select和poll在“醒着”的时候要遍历整个fd集合，而epoll在“醒着”的 时候只要判断一下就绪链表是否为空就行了，这节省了大量的CPU时间。这就是回调机制带来的性能提升。
- select，poll每次调用都要把fd集合从用户态往内核态拷贝一次，并且要把current往设备等待队列中挂一次，而epoll只要一次拷贝，而且把current往等待队列上挂也只挂一次（在epoll\_wait的开始，注意这里的等待队列并不是设备等待队列，只是一个epoll内部定义的等待队列）。这也能节省不少的开销。

## Java IO/NIO/AIO
事实上NIO是彻头彻尾的Blocking IO：调用select监听文件描述符需要block，select返回之后再次对ready的文件描述符进行操作需要block。而且相对于普通的Blocking IO它还多了一次系统调用。

但是它有两个好处：

- select可以同时监听多个文件描述符，而这些文件描述符其中的任意一个进入读就绪状态，select()函数就可以返回。这也是它被称为IO复用的原因。
- 如果select返回的时候，调用相应的Blocking IO操作一般不会“阻塞”，因为文件描述符已经是ready了。需要的时间只是将数据从内核copy到用户空间（或者相反）。

但是AIO就不一样了，它是真正的异步IO。当我们调用一个异步IO函数时，内核会马上返回。具体的I/O和数据的拷贝全部由内核来完成，我们的程序可以继续向下执行。当内核完成所有的I/O操作和数据拷贝后，内核将通知我们的程序。

当AIO函数返回的时候，不是文件描述符ready，然后你过去对他进行操作。而是数据完全ready！已经从内核copy到用户空间的缓冲区，或者反之。

Java 7中有三个新的异步通道：

- AsynchronousFileChannel: File AIO
- AsynchronousSocketChannel: TCP AIO，支持超时
- AsynchronousServerSocketChannel: TCP AIO
- AsynchronousDatagramChannel: UDP AIO

在使用新的异步IO时，主要有两种方式——Future轮询和Callback回调。

比如：从硬盘上的文件里读取100,000个字节。

### Future轮询
```java
try{
    Path file = Paths.get("/usr/argan/foobar.txt");

    AsynchronousFileChannel channel = AsynchronousFileChannel.open(file);

    ByteBuffer buffer = ByteBuffer.allocate(100_000);
    Future<Integer> result = channel.read(buffer, 0);

    while(!result.isDone()){
        // do something
    }

    Integer bytesRead = result.get();
    System.out.println("Bytes read [" + bytesRead + "]");
}catch(IOException | ExecutionException | InterruptedException e){
    System.err.println(e.getMessage());
}
```

其实底层JVM为执行这个任务创建了线程池和通道组。具体可以参考[AsynchronousFileChannel](http://docs.oracle.com/javase/7/docs/api/java/nio/channels/AsynchronousFileChannel.html)

> An AsynchronousFileChannel is associated with a thread pool to which tasks are submitted to handle I/O events and dispatch to completion handlers that consume the results of I/O operations on the channel. The completion handler for an I/O operation initiated on a channel is guaranteed to be invoked by one of the threads in the thread pool (This ensures that the completion handler is run by a thread with the expected identity). Where an I/O operation completes immediately, and the initiating thread is itself a thread in the thread pool, then the completion handler may be invoked directly by the initiating thread. When an AsynchronousFileChannel is created without specifying a thread pool then the channel is associated with a system-dependent default thread pool that may be shared with other channels. The default thread pool is configured by the system properties defined by the AsynchronousChannelGroup class.

### Callback回调
Future其实本质上还是轮循的方式，回调式才是真正的AIO。其基本思想是主线程会派一个侦查员CompletionHanlder到独立的线程中执行IO操作。这个侦查员将带着IO操作的结果返回到主线程中，这个结果会触发它自己的completed或者failed方法（你需要重写这两个方法）

- void completed(V result, A attachment) - executes if a task completes with a result of type V.
- void failed(Throwable e, A attachment) - executes if the task fails to complete due to Throwable e.

```java
try{ 
  Path file = Paths.get("/usr/argan/foobar.txt");
  AsynchronousFileChannel channel = AsynchronousFileChannel.open(file);

  ByteBuffer buffer = ByteBuffer.allocate(100_000);

  channel.read(buffer, 0, buffer, new CompletionHandler<Integer, ByteBuffer>(){
      public void completed(Integer result, ByteBuffer attachment){
          System.out.println("Bytes read [" + result + "]");
      }

      public void failed(Throwable exception, ByteBuffer attachment){
          System.err.println(exception.getMessage());
      }
  });
} catch(IOException e){ 
  System.err.println(e.getMessage());
}
```
上面的例子是基于文件的AsynchronousFileChannel，但是基于网络套接字的AsynchronousServerSocketChannel和AsynchronousSocketChannel也是一样的模式。

### Reference
1. [http://blog.arganzheng.me/posts/java-aio.html](http://blog.arganzheng.me/posts/java-aio.html)

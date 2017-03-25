#JVM profiling commands#

##jps：显示系统中所有Hotspot虚拟机进程##
###查看java进程信息###
用来查看所有的jvm进程，包括进程ID，进程启动的路径等。

```sh
jps -l
```

##jstat：收集Hotspot虚拟机各方面运行数据##
###查看内存使用、回收等信息###
利用JVM内建的指令对Java应用程序的资源和性能进行实时的命令行的监控，包括了对进程的classloader，compiler，gc情况；可以用来监视VM内存内的各种堆和非堆的大小及其内存使用量，以及加载类的数量。

```sh
jstat [option vmid [interval(s|ms) [count]]]
```

> ```sh
> eg:
> jstat -gc 2764 250 20
> jstat -gccause 2764 250 20
> jstat -gcnew 2764 250 20
> jstat -gcold 2764 250 20
> jstat -gccapacity 2764 250 20
> jstat -gcnewcapacity 2764 250 20
> jstat -gcoldcapacity 2764 250 20
> jstat -gcpermcapacity 2764 250 20
> jstat -gcutil 2764 250 20
> ```

###类加载情况的统计###

```
jstat -class 2764 250 20
```

###hotspot中JIT编译情况的统计##

```sh
jstat -compiler 2764 250 20
jstat -printcompilation 2764 250 20
```

##jstack：显示虚拟机的线程栈信息##
###查看线程运行情况、锁等信息###

```sh
jstack [option] vmid
```

```sh
jstack -F 2764   # 当请求不被响应时，强制输出线程堆栈
jstack -l 2764  # 除堆栈外，显示锁的附加信息
jstack -m 2764  # 混合模式，打印java和本地C++调用的堆栈信息
```

**Java程序中怎么获取所有线程的状态？怎么检查哪个线程处于死锁状态？**

JDK 1.5中Thread添加了getAllStackTraces()方法，可以获取虚拟机所有线程的StackTraceElement对象。

```java
for (Map.Entry<Thread, StackTraceElement[]> stackTrace : Thread.getAllStackTraces()
            .entrySet()) {
    Thread thread = stackTrace.getKey();
    StackTraceElement[] stack = stackTrace.getValue();
    if (thread.equals(Thread.currentThread())) {
        continue;
    }
    System.out.print("\n线程：" + thread.getName() + "\n");
    for (StackTraceElement element : stack) {
        System.out.print("\t" + element + "\n");
    }
}
```

如：

```sh
2017-03-25 17:22:04
Full thread dump Java HotSpot(TM) 64-Bit Server VM (25.112-b16 mixed mode):

"Attach Listener" #2040 daemon prio=9 os_prio=31 tid=0x00007fd8e90e9000 nid=0x1407 waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"DestroyJavaVM" #2039 prio=5 os_prio=31 tid=0x00007fd8e9294800 nid=0x1c03 waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"pool-1-thread-2029" #2037 prio=5 os_prio=31 tid=0x00007fd8e9294000 nid=0x102503 waiting on condition [0x00007000861f9000]
   java.lang.Thread.State: TIMED_WAITING (parking)
    at sun.misc.Unsafe.park(Native Method)
    - parking to wait for  <0x00000007997804e8> (a java.util.concurrent.SynchronousQueue$TransferStack)
    at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
    at java.util.concurrent.SynchronousQueue$TransferStack.awaitFulfill(SynchronousQueue.java:460)
    at java.util.concurrent.SynchronousQueue$TransferStack.transfer(SynchronousQueue.java:362)
    at java.util.concurrent.SynchronousQueue.poll(SynchronousQueue.java:941)
    at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1066)
    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1127)
    at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
    at java.lang.Thread.run(Thread.java:745)

.
.
.

"pool-1-thread-4" #12 prio=5 os_prio=31 tid=0x00007fd8e888d000 nid=0x5303 waiting on condition [0x000070000613e000]
   java.lang.Thread.State: TIMED_WAITING (parking)
    at sun.misc.Unsafe.park(Native Method)
    - parking to wait for  <0x00000007997804e8> (a java.util.concurrent.SynchronousQueue$TransferStack)
    at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
    at java.util.concurrent.SynchronousQueue$TransferStack.awaitFulfill(SynchronousQueue.java:460)
    at java.util.concurrent.SynchronousQueue$TransferStack.transfer(SynchronousQueue.java:362)
    at java.util.concurrent.SynchronousQueue.poll(SynchronousQueue.java:941)
    at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1066)
    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1127)
    at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
    at java.lang.Thread.run(Thread.java:745)

"pool-1-thread-3" #11 prio=5 os_prio=31 tid=0x00007fd8e80e9800 nid=0x5103 waiting on condition [0x000070000603b000]
   java.lang.Thread.State: TIMED_WAITING (parking)
    at sun.misc.Unsafe.park(Native Method)
    - parking to wait for  <0x00000007997804e8> (a java.util.concurrent.SynchronousQueue$TransferStack)
    at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
    at java.util.concurrent.SynchronousQueue$TransferStack.awaitFulfill(SynchronousQueue.java:460)
    at java.util.concurrent.SynchronousQueue$TransferStack.transfer(SynchronousQueue.java:362)
    at java.util.concurrent.SynchronousQueue.poll(SynchronousQueue.java:941)
    at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1066)
    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1127)
    at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
    at java.lang.Thread.run(Thread.java:745)

"pool-1-thread-2" #10 prio=5 os_prio=31 tid=0x00007fd8e888c000 nid=0x4f03 waiting on condition [0x0000700005f38000]
   java.lang.Thread.State: TIMED_WAITING (parking)
    at sun.misc.Unsafe.park(Native Method)
    - parking to wait for  <0x00000007997804e8> (a java.util.concurrent.SynchronousQueue$TransferStack)
    at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
    at java.util.concurrent.SynchronousQueue$TransferStack.awaitFulfill(SynchronousQueue.java:460)
    at java.util.concurrent.SynchronousQueue$TransferStack.transfer(SynchronousQueue.java:362)
    at java.util.concurrent.SynchronousQueue.poll(SynchronousQueue.java:941)
    at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1066)
    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1127)
    at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
    at java.lang.Thread.run(Thread.java:745)

"pool-1-thread-1" #9 prio=5 os_prio=31 tid=0x00007fd8e8887000 nid=0x4d03 waiting on condition [0x0000700005e35000]
   java.lang.Thread.State: TIMED_WAITING (parking)
    at sun.misc.Unsafe.park(Native Method)
    - parking to wait for  <0x00000007997804e8> (a java.util.concurrent.SynchronousQueue$TransferStack)
    at java.util.concurrent.locks.LockSupport.parkNanos(LockSupport.java:215)
    at java.util.concurrent.SynchronousQueue$TransferStack.awaitFulfill(SynchronousQueue.java:460)
    at java.util.concurrent.SynchronousQueue$TransferStack.transfer(SynchronousQueue.java:362)
    at java.util.concurrent.SynchronousQueue.poll(SynchronousQueue.java:941)
    at java.util.concurrent.ThreadPoolExecutor.getTask(ThreadPoolExecutor.java:1066)
    at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1127)
    at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:617)
    at java.lang.Thread.run(Thread.java:745)

"Service Thread" #8 daemon prio=9 os_prio=31 tid=0x00007fd8e8002000 nid=0x4903 runnable [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"C1 CompilerThread2" #7 daemon prio=9 os_prio=31 tid=0x00007fd8e908a800 nid=0x4703 waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"C2 CompilerThread1" #6 daemon prio=9 os_prio=31 tid=0x00007fd8e8816800 nid=0x4503 waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"C2 CompilerThread0" #5 daemon prio=9 os_prio=31 tid=0x00007fd8e903f000 nid=0x4303 waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"Signal Dispatcher" #4 daemon prio=9 os_prio=31 tid=0x00007fd8e903c000 nid=0x4103 runnable [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

"Finalizer" #3 daemon prio=8 os_prio=31 tid=0x00007fd8e980c800 nid=0x3103 in Object.wait() [0x0000700005720000]
   java.lang.Thread.State: WAITING (on object monitor)
    at java.lang.Object.wait(Native Method)
    - waiting on <0x00000007997de4b8> (a java.lang.ref.ReferenceQueue$Lock)
    at java.lang.ref.ReferenceQueue.remove(ReferenceQueue.java:143)
    - locked <0x00000007997de4b8> (a java.lang.ref.ReferenceQueue$Lock)
    at java.lang.ref.ReferenceQueue.remove(ReferenceQueue.java:164)
    at java.lang.ref.Finalizer$FinalizerThread.run(Finalizer.java:209)

"Reference Handler" #2 daemon prio=10 os_prio=31 tid=0x00007fd8e9028800 nid=0x2f03 in Object.wait() [0x000070000561d000]
   java.lang.Thread.State: WAITING (on object monitor)
    at java.lang.Object.wait(Native Method)
    - waiting on <0x00000007997f0378> (a java.lang.ref.Reference$Lock)
    at java.lang.Object.wait(Object.java:502)
    at java.lang.ref.Reference.tryHandlePending(Reference.java:191)
    - locked <0x00000007997f0378> (a java.lang.ref.Reference$Lock)
    at java.lang.ref.Reference$ReferenceHandler.run(Reference.java:153)

"VM Thread" os_prio=31 tid=0x00007fd8e9024000 nid=0x2d03 runnable 

"GC task thread#0 (ParallelGC)" os_prio=31 tid=0x00007fd8e8810000 nid=0x2503 runnable 

"GC task thread#1 (ParallelGC)" os_prio=31 tid=0x00007fd8e8810800 nid=0x2703 runnable 

"GC task thread#2 (ParallelGC)" os_prio=31 tid=0x00007fd8e8811000 nid=0x2903 runnable 

"GC task thread#3 (ParallelGC)" os_prio=31 tid=0x00007fd8e8812000 nid=0x2b03 runnable 

"VM Periodic Task Thread" os_prio=31 tid=0x00007fd8e8018800 nid=0x4b03 waiting on condition 

JNI global references: 22
```


##jmap：用于生成虚拟机的内存快照信息##
###查看堆中对象的情况###
用来监视进程运行中的jvm物理内存的占用情况，该进程内存内，所有对象的情况，例如产生了哪些对象，对象数量。当系统崩溃时，jmap 可以从core文件或进程中获得内存的具体匹配情况，包括Heap size, Perm size等。

```sh
jmap [option] pid
jmap [option] executable core
jmap [option] [server-id@]remote-hostname-or-ip
```

```sh
options:
-dump：[live,]format=b,file=<filename> 使用hprof二进制形式,输出jvm的heap内容到文件=. live子选项是可选的，假如指定live选项,那么只输出活的对象到文件；
-finalizerinfo：打印正等候回收的对象的信息；
-heap：打印heap的概要信息，GC使用的算法，heap的配置及wise heap的使用情况；
-histo：[:live] 打印每个class的实例数目,内存占用,类全名信息. VM的内部类名字开头会加上前缀”*”. 如果live子参数加上后,只统计活的对象数量；
-clstats：打印classloader和jvm heap长久层的信息。 包含每个classloader的名字,父classloader和加载的class数量。另外,内部String的数量和占用内存数也会打印出来；
-F：强迫.在pid没有相应的时候使用-dump或者-histo参数。在这个模式下,live子参数无效；
-h： | -help 打印辅助信息；
-J ：传递参数给jmap启动的jvm；
```

```sh
#显示java进程内存使用的相关信息 
jmap pid #打印内存使用的摘要信息 
jmap –heap pid #java heap信息 
jmap -histo:live pid #统计对象count ，live表示在使用 
jmap -histo pid > mem.txt #打印比较简单的各个有多少个对象占了多少内存的信息，一般重定向的文件 
jmap -dump:format=b,file=mem.dat pid #将内存使用的详细情况输出到mem.dat 文件 
```

###分析堆转储文件###
是用来分析java堆的命令，可以将堆中的对象以html的形式显示出来，包括对象的数量，大小等等，并支持对象查询语言。

如：

```sh
racing >>> jmap -dump:live,format=b,file=heap.map 19585
Dumping heap to /Users/racing/Documents/workspace/note/heap.map ...
Heap dump file created
ychen.local/Users/racing/Documents/workspace/note  - - - - - - - - - - - - - - - - - 15-08-03 22:36
racing >>> jhat heap.map
Reading from heap.map...
Dump file created Mon Aug 03 22:36:52 CST 2015
Snapshot read, resolving...
Resolving 11680 objects...
Chasing references, expect 2 dots..
Eliminating duplicate references..
Snapshot resolved.
Started HTTP server on port 7000
Server is ready.
# 最后两句话说明开启了http服务，在7000端口，然后打开浏览器输入http://localhost:7000就能看到jhat结果
```

```sh
C:\Users\Administrator>jmap -heap 104292
Attaching to process ID 104292, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.121-b13

using thread-local object allocation.
Parallel GC with 8 thread(s)

Heap Configuration:
   MinHeapFreeRatio         = 0
   MaxHeapFreeRatio         = 100
   MaxHeapSize              = 4276092928 (4078.0MB)
   NewSize                  = 89128960 (85.0MB)
   MaxNewSize               = 1425014784 (1359.0MB)
   OldSize                  = 179306496 (171.0MB)
   NewRatio                 = 2
   SurvivorRatio            = 8
   MetaspaceSize            = 21807104 (20.796875MB)
   CompressedClassSpaceSize = 1073741824 (1024.0MB)
   MaxMetaspaceSize         = 17592186044415 MB
   G1HeapRegionSize         = 0 (0.0MB)

Heap Usage:
PS Young Generation
Eden Space:
   capacity = 505413632 (482.0MB)
   used     = 138800392 (132.37036895751953MB)
   free     = 366613240 (349.62963104248047MB)
   27.462732148862973% used
From Space:
   capacity = 38273024 (36.5MB)
   used     = 20185136 (19.250045776367188MB)
   free     = 18087888 (17.249954223632812MB)
   52.73985144210188% used
To Space:
   capacity = 39321600 (37.5MB)
   used     = 0 (0.0MB)
   free     = 39321600 (37.5MB)
   0.0% used
PS Old Generation
   capacity = 179306496 (171.0MB)
   used     = 35328280 (33.691673278808594MB)
   free     = 143978216 (137.3083267211914MB)
   19.702732911583972% used

1918 interned Strings occupying 169936 bytes.
```


##jinfo：显示虚拟机的配置信息##
jinfo可以**输出并修改**运行时的java进程的options。用处比较简单，用于输出JAVA系统参数及命令行参数。用法是`jinfo -opt  pid` 如：查看2788的MaxPerm大小可以用`jinfo -flag MaxPermSize 2788`。

```sh
Usage:
    jinfo [option] <pid>
        (to connect to running process)
    jinfo [option] <executable <core>
        (to connect to a core file)
    jinfo [option] [server_id@]<remote server IP or hostname>
        (to connect to remote debug server)

where <option> is one of:
    -flag <name>         to print the value of the named VM flag
    -flag [+|-]<name>    to enable or disable the named VM flag
    -flag <name>=<value> to set the named VM flag to the given value
    -flags               to print VM flags
    -sysprops            to print Java system properties
    <no option>          to print both of the above
    -h | -help           to print this help message
```

如：

```sh
C:\Users\Administrator>jinfo -flags 103756
Attaching to process ID 103756, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.121-b13
Non-default VM flags: -XX:-BytecodeVerificationLocal -XX:-BytecodeVerificationRemote -XX:CICompilerCount=4 -XX:-ClassUnloading -XX:ConcGCThreads=2 -XX:+DisableExplicitGC -XX:G1HeapRegionSize=1048576 -XX:InitialHeapSize=1073741824 -XX:MarkStackSize=4194304 -XX:MaxHeapSize=1342177280 -XX:MaxNewSize=805306368 -XX:MinHeapDeltaBytes=1048576 -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:+UseFastUnorderedTimeStamps -XX:+UseG1GC -XX:-UseLargePagesIndividualAllocation -XX:+UseStringDeduplication
Command line:  -Declipse.p2.max.threads=10 -Doomph.update.url=http://download.eclipse.org/oomph/updates/milestone/latest -Doomph.redirection.index.redirection=index:/->http://git.eclipse.org/c/oomph/org.eclipse.oomph.git/plain/setups/ -Xverify:none -XX:PermSize=128m -XX:MaxPermSize=256m -XX:+DisableExplicitGC -Xnoclassgc -Dosgi.requiredJavaVersion=1.8 -XX:+UseG1GC -XX:+UseStringDeduplication -Dosgi.requiredJavaVersion=1.8 -Xms1024m -Xmx1280m
```

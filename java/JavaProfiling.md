##JVM profiling commands:##

###查看java进程信息###
用来查看所有的jvm进程，包括进程ID，进程启动的路径等。

```sh
jps -l
```

###查看内存使用、回收等信息###
利用JVM内建的指令对Java应用程序的资源和性能进行实时的命令行的监控，包括了对进程的classloader，compiler，gc情况；可以用来监视VM内存内的各种堆和非堆的大小及其内存使用量，以及加载类的数量。

```sh
jstat [option vmid [interval(s|ms) [count]]]
```
> ```sh
eg:
jstat -gc 2764 250 20
jstat -gccause 2764 250 20
jstat -gcnew 2764 250 20
jstat -gcold 2764 250 20
jstat -gccapacity 2764 250 20
jstat -gcnewcapacity 2764 250 20
jstat -gcoldcapacity 2764 250 20
jstat -gcpermcapacity 2764 250 20
jstat -gcutil 2764 250 20
jstat -class 2764 250 20
jstat -compiler 2764 250 20
jstat -printcompilation 2764 250 20
```

###查看线程运行情况、锁等信息###

```sh
jstack [option] vmid
```
> ```sh
> eg:
jstack -F 2764
jstack -l 2764
```

###查看堆中对象的情况###
用来监视进程运行中的jvm物理内存的占用情况，该进程内存内，所有对象的情况，例如产生了哪些对象，对象数量。当系统崩溃时，jmap 可以从core文件或进程中获得内存的具体匹配情况，包括Heap size, Perm size等。

```sh
jmap [option] pid
jmap [option] executable core
jmap [option] [server-id@]remote-hostname-or-ip
```

```sh
#显示java进程内存使用的相关信息 
jmap pid #打印内存使用的摘要信息 
jmap –heap pid #java heap信息 
jmap -histo:live pid #统计对象count ，live表示在使用 
jmap -histo pid >mem.txt #打印比较简单的各个有多少个对象占了多少内存的信息，一般重定向的文件 
jmap -dump:format=b,file=mem.dat pid #将内存使用的详细情况输出到mem.dat 文件 
```

###分析堆转储文件###
是用来分析java堆的命令，可以将堆中的对象以html的形式显示出来，包括对象的数量，大小等等，并支持对象查询语言。

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
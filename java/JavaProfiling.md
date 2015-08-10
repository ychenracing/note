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
# 类加载情况的统计
jstat -class 2764 250 20
# hotspot中JIT编译情况的统计
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

###jinfo###
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
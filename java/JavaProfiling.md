##JVM profiling commands:##

###查看java进程信息###
```sh
jps -l
```

###查看内存使用、回收等信息###
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
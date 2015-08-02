##Linux链接概念##
Linux链接分两种，一种被称为硬链接（`Hard Link`），另一种被称为符号链接（软链接）（`Symbolic Link`）。默认情况下，`ln`命令产生硬链接，`ln -s`产生软链接。

###硬链接###
硬链接指通过索引节点来进行链接。在Linux的文件系统中，保存在磁盘分区中的文件不管是什么类型都给它分配一个编号，称为索引节点号(`Inode Index`)。在Linux中，多个文件名指向同一索引节点是存在的。一般这种链接就是硬链接。硬链接的作用是允许一个文件拥有多个有效路径名，这样用户就可以建立硬链接到重要文件，以防止“误删”的功能。其原因如上所述，因为对应该目录的索引节点有一个以上的链接。只删除一个链接并不影响索引节点本身和其它的链接，只有当最后一个链接被删除后，文件的数据块及目录的链接才会被释放。也就是说，文件真正删除的条件是与之相关的所有硬链接文件均被删除。

###软链接###
另外一种链接称之为符号链接（`Symbolic Link`），也叫软链接。软链接文件类似于Windows的快捷方式。它实际上是一个特殊的文件。在符号链接中，文件实际上是一个文本文件，其中包含的有另一文件的位置信息。

##通过实验加深理解##
```
[ychen@racing]$ touch f1          #创建一个测试文件f1
[ychen@racing]$ ln f1 f2          #创建f1的一个硬链接文件f2
[ychen@racing]$ ln -s f1 f3       #创建f1的一个符号链接文件f3
[ychen@racing]$ ls -li            # -i参数显示文件的inode节点信息
total 0
9797648 -rw-r--r--  2 ychen oinstall 0 Apr 21 08:11 f1
9797648 -rw-r--r--  2 ychen oinstall 0 Apr 21 08:11 f2
9797649 lrwxrwxrwx  1 ychen oinstall 2 Apr 21 08:11 f3 -> f1
```

从上面的结果中可以看出，硬链接文件f2与原文件f1的`inode`节点相同，均为9797648，然而符号链接文件的`inode`节点不同。

```
[ychen@racing]$ echo "I am f1 file" >>f1
[ychen@racing]$ cat f1
I am f1 file
[ychen@racing]$ cat f2
I am f1 file
[ychen@racing]$ cat f3
I am f1 file
[ychen@racing]$ rm -f f1
[ychen@racing]$ cat f2
I am f1 file
[ychen@racing]$ cat f3
cat: f3: No such file or directory
```

通过上面的测试可以看出：当删除原始文件f1后，硬链接f2不受影响，但是符号链接f1文件无效。

##总结##
依此可以做一些相关的测试，可以得到以下全部结论：
> 1. 删除符号链接f3,对f1,f2无影响；
> 2. 删除硬链接f2，对f1,f3也无影响；
> 3. 删除原文件f1，对硬链接f2没有影响，导致符号链接f3失效；
> 4. 同时删除原文件f1,硬链接f2，整个文件会真正的被删除。

## rename ##
1. 用法一：`rename arg1 arg2 arg3`。arg1表示原字符串：将文件名需要替换的字符串；arg2表示目标字符串：将文件名中含有的原字符替换成目标字符串；arg3表示文件名列表：指定要改变的文件名列表。其中，arg3使用的是glob模式，即?表示单个字符，\+表示一个或多个字符，\*表示0个或多个字符。
2. 用法二：`rename 'arg1' arg2`。arg1表示正则表达式，arg2表示要改变的文件名列表。arg2是glob模式，与用法一中的arg3一致。

```sh
# 假设当前文件夹下含有test.py, test.pl, test.sh, test.java, 
# test.js, test.cpp, test.css, test.r, test.html这些文件。

>>> rename test test1 test.p?
# 则test.py变成了test1.py，test.pl变成了test1.pl

>>> rename test test2 test*
# 则当前文件夹下所有文件名中的test都变成了test2

>>> rename 's/est/EST/' *
# 把所有文件名中的est替换成EST

>>> rename 's/$/.txt/' test21.p?
# 把test21.py和test21.pl的末尾都加上.txt后缀

>>> rename 's/.txt//' *
# 把所有文件名末尾的.txt后缀删掉
```
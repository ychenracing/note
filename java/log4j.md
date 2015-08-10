一般都提供了这样5个日志级别：

- Debug
- Info
- Warn
- Error
- Fatal

一个等级比一个高，但是在具体开发中，应该如何选择适应的等级

###Debug###
这 个级别最低的东东，一般的来说，在系统实际运行过程中，一般都是不输出的。

因此这个级别的信息，可以随意的使用，任何觉得有利于在调试时更详细的了解系统 运行状态的东东，比如变量的值等等，都输出来看看也无妨。

当然，在每一个 Debug 调用之前，一定要加上 If 判断。

###Info###
这个应该用来反馈系统的当前状态给最终用户的，所以，在这里输出的信息，应该对最终用户具有实际意义，也就是最终用户要能够看得明白是什么意思才行。

从某种角度上说，Info 输出的信息可以看作是软件产品的一部分（就像那些交互界面上的文字一样），所以需要谨慎对待，不可随便。

###Warn、Error、Fatal###
警告、错误、严重错误，这三者应该都在系统运行时检测到了一个不正常的状态，他们之间的区别，要区分还真不是那么简单的事情。我大致是这样区分的：

所谓警告，应该是这个时候进行一些修复性的工作，应该还可以把系统恢复到正常状态中来，系统应该可以继续运行下去。

所谓错误，就是说可以进行一些修复性的工作，但无法确定系统会正常的工作下去，系统在以后的某个阶段，很可能会因为当前的这个问题，导致一个无法修复的错误（例如宕机），但也可能一直工作到停止也不出现严重问题。

所谓Fatal，那就是相当严重的了，可以肯定这种错误已经无法修复，并且如果系统继续运行下去的话，可以肯定必然会越来越乱。这时候采取的最好的措施不是试图将系统状态恢复到正常，而是尽可能地保留系统有效数据并停止运行。

也就是说，选择 Warn、Error、Fatal 中的具体哪一个，是根据当前的这个问题对以后可能产生的影响而定的，如果对以后基本没什么影响，则警告之，如果肯定是以后要出严重问题的了，则Fatal之，拿不准会怎么样，则 Error 之。

web.xml中添加：

```xml
   <context-param>     
      <param-name>log4jConfigLocation</param-name>     
      <param-value>/WEB-INF/props/log4j.properties</param-value>     
   </context-param>     
   <context-param>     
      <param-name>log4jRefreshInterval</param-name>     
      <param-value>6000</param-value>     
   </context-param>

    <listener> 
      <listener-class> 
         org.springframework.web.util.Log4jConfigListener 
      </listener-class> 
   </listener>
```


```sh
# log4j.properties
### set log levels ###
log4j.rootLogger = debug, stdout, D, E

### 输出到控制台 ###
log4j.appender.stdout = org.apache.log4j.ConsoleAppender
log4j.appender.stdout.Target = System.out
log4j.appender.stdout.layout = org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern =  %d{ABSOLUTE} %5p %c{1}:%L-%m%n

### 输出到日志文件 ###
log4j.appender.D = org.apache.log4j.DailyRollingFileAppender
log4j.appender.D.encoding=UTF-8
log4j.appender.D.File = logs/ychen.log
log4j.appender.D.MaxFileSize=10MB 
log4j.appender.D.DatePattern = '.'yyyy-MM-dd 
log4j.appender.D.Append = true
log4j.appender.D.Threshold = DEBUG ## 输出DEBUG级别以上的日志
log4j.appender.D.layout = org.apache.log4j.PatternLayout
log4j.appender.D.layout.ConversionPattern = [%p] %-d{yyyy-MM-dd HH:mm:ss} [%t:%r]-[%p] %m%n

### 保存异常信息到单独文件 ###
log4j.appender.E = org.apache.log4j.DailyRollingFileAppender
log4j.appender.E.encoding=UTF-8
## 异常日志文件名
log4j.appender.E.File = logs/ychen-error.log
log4j.appender.E.MaxFileSize=10MB 
log4j.appender.E.DatePattern = '.'yyyy-MM-dd 
log4j.appender.E.Append = true
log4j.appender.E.Threshold = ERROR ## 只输出ERROR级别以上的日志!!!
log4j.appender.E.layout = org.apache.log4j.PatternLayout
log4j.appender.E.layout.ConversionPattern = [%p] %-d{yyyy-MM-dd HH:mm:ss} [%l:%c:%t:%r]-[%p] %m%n
```
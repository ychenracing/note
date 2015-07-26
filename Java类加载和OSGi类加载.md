#类加载机制#
###双亲委派模型###
![双亲委派模型](http://www.ibm.com/developerworks/cn/java/j-lo-classloader/image001.jpg "双亲委派模型")

1. 最顶层的为`Bootstrap ClassLoader`，又名启动类加载器，加载`%JAVA_HOME%\lib`下的类，自己写的java应用程序访问不到该类加载器。由于双亲委派模型，所有的类加载请求都会被委派给该类加载器加载，如果该类加载器加载不了，再退回。
2. 第二层的为`Extension ClassLoader`，又名扩展类加载器，加载`%AJVA_HOME%\lib\ext`下的Java类。
3. 第三层的为`Application ClassLoader`，叫做应用程序类加载器，由于其是getSystemClassLoader()的返回值，所以又叫做系统类加载器。
4. 下面的都是用户自定义的类加载器。  

###JDK中类加载器源码###
```java
protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // First, check if the class has already been loaded
        Class<?> c = findLoadedClass(name);
        if (c == null) {
            long t0 = System.nanoTime();
            try {
                if (parent != null) {
                    c = parent.loadClass(name, false);
                } else {
                    c = findBootstrapClassOrNull(name);
                }
            } catch (ClassNotFoundException e) {
                // ClassNotFoundException thrown if class not found
                // from the non-null parent class loader
            }

            if (c == null) {
                // If still not found, then invoke findClass in order
                // to find the class.
                long t1 = System.nanoTime();
                c = findClass(name);

                // this is the defining class loader; record the stats
                sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                sun.misc.PerfCounter.getFindClasses().increment();
            }
        }
        if (resolve) {
            resolveClass(c);
        }
        return c;
    }
}
```

阅读上面代码可以看出：

1. 遇到类加载请求时，首先查找已加载的类，找到的话会解析返回，没有则2。
2. 如果父类加载器不为空，委托给父类加载器加载，否则自己就是`Bootstrap ClassLoader`，查找`Bootstrap ClassLoader`，让其加载。
3. 要是2也找不到，则抛出`ClassNotFoundException`，吞掉，用加载自己的类加载器加载。

###JDK中ClassLoader中比较重要的方法###

| **方法**	  |    **说明**   |
|----------:|:-------------|
|getParent()|返回该类加载器的父类加载器。|
|loadClass(String name)|加载名称为name的类，返回的结果是java.lang.Class类的实例，会抛出ClassNotFoundException。|
|findClass(String name)|查找名称为 name的类，返回的结果是java.lang.Class类的实例。|
|findLoadedClass(String name)|查找名称为name的已经被加载过的类，返回的结果是java.lang.Class类的实例。|
|defineClass(String name, byte[] b, int off, int len)|把字节数组b中的内容转换成Java类，返回的结果是java.lang.Class类的实例。这个方法被声明为 final的，会抛出NoClassDefFoundError。|
|resolveClass(Class<?> c)|链接指定的Java类。|

其中，需要非常明确两个方法：**loadClass**和**defineClass**。loadClass是启动类加载过程的那个动作，defineClass是真正加载类的动作。如果类A中使用到了类B，则启动类B的类加载动作是由加载了类A的类加载器的loadClass方法执行的，而真正执行加载类B的类加载器可能不是加载了类A的类加载器。loadClass抛出`ClassNotFoundException`，defineClass抛出`NoClassDefFoundError`。

在前面介绍类加载器的双亲委派模型的时候，提到过类加载器会首先委派给其它类加载器来尝试加载某个类。这就意味着真正完成类的加载工作的类加载器和启动这个加载过程的类加载器，有可能不是同一个。真正完成类的加载工作是通过调用 defineClass来实现的；而启动类的加载过程是通过调用loadClass来实现的。前者称为一个类的定义加载器`defining loader`，后者称为初始加载器`initiating loader`。在Java虚拟机判断两个类是否相同的时候，使用的是类的定义加载器。也就是说，哪个类加载器启动类的加载过程并不重要，重要的是最终定义这个类的加载器。两种类加载器的关联之处在于：一个类的定义加载器是它引用的其它类的初始加载器。

###定义自己的类加载器###

虽然在绝大多数情况下，系统默认提供的类加载器实现已经可以满足需求。但是在某些情况下，还是需要为应用开发出自己的类加载器。比如自己的应用通过网络来传输Java类的字节代码，为了保证安全性，这些字节代码经过了加密处理。这个时候就需要自己的类加载器来从某个网络地址上读取加密后的字节代码，接着进行解密和验证，最后定义出要在Java虚拟机中运行的类来。下面将通过实例来说明类加载器的开发。  

**文件系统类加载器**  

第一个类加载器用来加载存储在文件系统上的Java字节代码。完整的实现如：

```java
public class FileSystemClassLoader extends ClassLoader { 

    private String rootDir; 

    public FileSystemClassLoader(String rootDir) { 
        this.rootDir = rootDir; 
    } 

    protected Class<?> findClass(String name) throws ClassNotFoundException { 
        byte[] classData = getClassData(name); 
        if (classData == null) { 
            throw new ClassNotFoundException(); 
        } 
        else { 
            return defineClass(name, classData, 0, classData.length); 
        } 
    } 

    private byte[] getClassData(String className) { 
        String path = classNameToPath(className); 
        try { 
            InputStream ins = new FileInputStream(path); 
            ByteArrayOutputStream baos = new ByteArrayOutputStream(); 
            int bufferSize = 4096; 
            byte[] buffer = new byte[bufferSize]; 
            int bytesNumRead = 0; 
            while ((bytesNumRead = ins.read(buffer)) != -1) { 
                baos.write(buffer, 0, bytesNumRead); 
            } 
            return baos.toByteArray(); 
        } catch (IOException e) { 
            e.printStackTrace(); 
        } 
        return null; 
    } 

    private String classNameToPath(String className) { 
        return rootDir + File.separatorChar 
                + className.replace('.', File.separatorChar) + ".class"; 
    } 
}
```
如上所示，类`FileSystemClassLoader`继承自类`java.lang.ClassLoader`。在ClassLoader方法表中列出的`java.lang.ClassLoader`类的常用方法中，一般来说，自己开发的类加载器只需要覆写`findClass(String name)`方法即可。

`java.lang.ClassLoader`类的方法`loadClass()`封装了双亲委派模型的实现。该方法会首先调用`findLoadedClass()`方法来检查该类是否已经被加载过；如果没有加载过的话，会调用父类加载器的`loadClass()`方法来尝试加载该类；如果父类加载器无法加载该类的话，就调用`findClass()`方法来查找该类。因此，为了保证类加载器都正确实现委派模型，在开发自己的类加载器时，最好不要覆写`loadClass()`方法，而是覆写 `findClass()`方法。

类`FileSystemClassLoader`的`findClass()`方法首先根据全类名在硬盘上查找类的字节代码文件（.class 文件），然后读取该文件内容，最后通过`defineClass()`方法来把这些字节代码转换成`java.lang.Class`类的实例。

###Tomcat类加载###
跟其他主流的Java Web服务器一样，Tomcat也拥有不同的自定义类加载器，达到对各种资源库的控制。一般来说，Java Web服务器需要解决以下四个问题：

- 同一个Web服务器里，各个Web项目之间各自使用的Java类库要互相隔离。
- 同一个Web服务器里，各个Web项目之间可以提供共享的Java类库。
- 服务器为了不受Web项目的影响，应该使服务器的类库与应用程序的类库互相独立。
- 对于支持JSP的Web服务器，应该支持热插拔（hotswap）功能。
对于以上几个问题，如果单独使用一个类加载器明显是达不到效果的，必须根据实际使用若干个自定义类加载器。

Tomcat5类加载机制：  
![Tomcat5类加载](http://imtiger.net/images/2013/10/30/tomcat-classloader.png "Tomcat5类加载")
Tomcat6类加载机制：  
![Tomcat6类加载](http://7xipn4.com1.z0.glb.clouddn.com/assets/jvm/classloader/tomcat6.jpg "Tomcat6类加载")
Tomcat7类加载机制：  
![Tomcat7类加载](http://7xipn4.com1.z0.glb.clouddn.com/assets/jvm/classloader/tomcat7.png "Tomcat7类加载")

Tomcat5,6,7的ClassLoader结构略有不同。

- Tomcat6中将CommonClassLoader，CatalinaClassLoader，SharedClassLoader合并，就一个CommonClassLoader。
- Tomcat7中没有ExtensionClassLoader。

首先看前三个问题:  
从上图可以看出，为了解决jar隔离和共享的问题。对于每个webapp,Tomcat都会创建一个WebAppClassLoader来加载应用，这样就保证了每个应用加载进来的class都是不同的(因为ClassLoader不同)! 而共享的jar放在tomcat-home/lib目录下，由CommonClassLoader来加载。通过双亲委托模式，提供给其下的所有webapp共享。

**特别说明**  
对于WebAppClassLoader是违反双亲委托模型的。如果加载的是jre或者servlet api则依然是双亲委托模型。 而如果不是的话，则会先尝试自行加载，如果找不到再委托父加载器加载。 这个应该是可以理解的，因为应用的class是由WebAppClassLoader加载的，是项目私有的。

##OSGi类加载机制##
OSGi为了实现模块化的功能，自己实现了一套网状的类加载模式：  
![OSGi网状类加载模式](http://7xipn4.com1.z0.glb.clouddn.com/assets/jvm/classloader/osgi01.png "OSGi网状类加载模式")

###OSGi类加载流程###
![OSGi类加载流程](http://7xipn4.com1.z0.glb.clouddn.com/assets/jvm/classloader/osgi02.gif "OSGi类加载流程")
Step 1:  
> 检查是否java.，或者在bootdelegation中定义
>> 当bundle类加载器需要加载一个类时，首先检查包名是否以java.开头，或者是否在一个特定的配置文件（org.osgi.framework.bootdelegation）中定义。 如果是，则bundle类加载器立即委托给父类加载器（通常是Application类加载器）。
这么做有两个原因：

>> - 唯一能够定义java.*包的类加载器是bootstrap类加载器，这个规则是JVM要求的。如果OSGI bundle类加载器试图加载这种类，则会抛Security Exception。
>> - 一些JVM错误地假设父加载器委托永远会发生，内部VM类就能够通过任何类加载器找到特定的其他内部类。所以OSGi提供了org.osgi.framework.bootdelegation属性，允许对特定的包（即那些内部VM类）使用父加载器委托。  

Step 2:  
> 检查是否在Import-Package中声明  
>> 检查是否在Import-Package中声明。如果是，则找到导出包的bundle，将类加载请求委托给该bundle的类加载器。如此往复。

Step 3:  
> 检查是否在Require-Bundle中声明  
>> 检查是否在Require-Bundle中声明。如果是，则将类加载请求委托给required bundle的类加载器。

Step 4:  
> 检查是否bundle内部类  
>> 检查是否是该bundle内部的类，即当前JAR文件中的类。

Step5:  
> 检查fragment  
>> 搜索可能附加在当前bundle上的fragment中的内部类。

**什么是fragment？**  
Fragment bundle是OSGi 4引入的概念，它是一种不完整的bundle，必须要附加到一个host bundle上才能工作；fragment能够为host bundle添加类或资源，在运行时，fragment中的类会合并到host bundle的内部classpath中。

OSGi 中的每个模块（bundle）都包含 Java 包和类。模块可以声明它所依赖的需要导入（import）的其它模块的 Java 包和类（通过 Import-Package），也可以声明导出（export）自己的包和类，供其它模块使用（通过 Export-Package）。也就是说需要能够隐藏和共享一个模块中的某些 Java 包和类。这是通过 OSGi 特有的类加载器机制来实现的。OSGi 中的每个模块都有对应的一个类加载器。它负责加载模块自己包含的 Java 包和类。当它需要加载 Java 核心库的类时（以 java开头的包和类），它会代理给父类加载器（通常是启动类加载器）来完成。当它需要加载所导入的 Java 类时，它会代理给导出此 Java 类的模块来完成加载。模块也可以显式的声明某些 Java 包和类，必须由父类加载器来加载。只需要设置系统属性 org.osgi.framework.bootdelegation的值即可。

假设有两个模块 bundleA 和 bundleB，它们都有自己对应的类加载器 classLoaderA 和 classLoaderB。在 bundleA 中包含类 com.bundleA.Sample，并且该类被声明为导出的，也就是说可以被其它模块所使用的。bundleB 声明了导入 bundleA 提供的类 com.bundleA.Sample，并包含一个类 com.bundleB.NewSample继承自 com.bundleA.Sample。在 bundleB 启动的时候，其类加载器 classLoaderB 需要加载类 com.bundleB.NewSample，进而需要加载类 com.bundleA.Sample。由于 bundleB 声明了类 com.bundleA.Sample是导入的，classLoaderB 把加载类 com.bundleA.Sample的工作代理给导出该类的 bundleA 的类加载器 classLoaderA。classLoaderA 在其模块内部查找类 com.bundleA.Sample并定义它，所得到的类 com.bundleA.Sample实例就可以被所有声明导入了此类的模块使用。对于以 java开头的类，都是由父类加载器来加载的。如果声明了系统属性 org.osgi.framework.bootdelegation=com.example.core.*，那么对于包 com.example.core中的类，都是由父类加载器来完成的。

The END!


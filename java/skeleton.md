##大端小端##
（Java采用的Big Endian字节序，所有的网络协议也都是采用Big Endian字节序来进行传输的）计算机中的数据存放是从内存的低位地址开始的，比如，从地址为0的地方开始存放数据，接着从地址为1的地方开始存放数据，...，则大端模式和小端模式为，

- 大端模式：数据的**高**位存放在**低**位地址的内存中（即高位先存）。
- 小端模式：数据的**低**位存放在**低**位地址的内存中（即低位先存）。

数据ox1234的存放情况为，  
![大端小端](img/1.png "大端小端")  
只要记住：大端是数据高位和地址高位相反（不一致），小端则一致。

![](img/2.png)  
另一边是空的，当然不浪费一个对象来引用之。

##初始化与清理（机制和流程）##
- 构建和初始化是捆绑在一起的，对于方法重载的两个（或以上）方法，参数的类型、个数、**顺序**总有一项是不同的，不能通过返回值来区分重载方法，这是因为有时候你调用一个方法并不关心它的返回值而是关心它的执行过程。**除了构造器之外，编译器禁止其他任何方法中调用构造器**。
- finalize()存在的意义？finalize()应该怎么用？用在哪里？
- 理解垃圾回收器的工作方式：引用计数的方法（每个对象都有一个引用计数器，当有引用连接至对象时，该引用计数器加1，引用离开作用域或被置null时，引用计数器减1，引用计数为0时对象被清理）。引用计数方法只适合用来理解垃圾回收器的工作方式，但是还没有被应用在任何一种JVM中，存在循环引用的问题。
- 初始化顺序：假设有个名为Dog的类:
    1. 【加载】当首次创建Dog的对象或者Dog类的静态方法/静态域（非编译期常量）被首次访问时，java解释器必须查找类的路径，找到Dog.class文件，然后载入Dog.class（这会创建一个Class对象，然后对这个Class对象进行初始化。每个类都有一个Class对象，类的对象由这个Class对象创建）。（由此得知什么时候会载入一个类的字节码，从下面步骤也得知，载入字节码之后会发生什么事）。
    2. 【链接】验证类中的字节码，为静态区域分配存储空间。接下来，【初始化，对一个类进行初始化，也叫对一个Class对象进行初始化】。有关**静态初始化**的所有动作都会执行。（静态块和静态域按顺序执行，也就是说，静态初始化发生在new操作在堆上为对象分配存储空间之前）。
    3. 当用new Dog()创建对象时，首先将在堆上为对象分配足够的存储空间。再次注意，非静态块初始化发生在new操作之后！！！（因为静态块静态区域的内容是在常量池的，所以初始化比较早。非静态块的内容是在对象的空间上的，属于堆的，所以，需要先new分配空间后，才能进行初始化）。
    4. 这块存储空间清零（二进制的0），即自动的把对象的所有基本数据类型设置成了默认值。
    5. 执行所有出现在字段定义处的初始化动作。
    6. 执行构造器。
        - 子类无论什么构造器，内部都会自动调用父类的默认构造器（即无参构造器），如果父类没有无参构造器，则子类构造器出错，**需要强制调用父类的构造器**，调用父类的有参无参构造器均可。 
        - 子类构造器执行，必须先执行父类的构造器，子类想要初始化，必须先初始化父类。

所以总的构造顺序是：<font color="red">父类静态块 --> 然后是子类静态块 --> 父类自由块 --> 父类构造函数块 --> 子类自由块 --> 子类构造函数块</font>，很容易忽略但是是事实的点：父类构造器在子类成员初始化前！！！！！

###static###
父类中的static域只会存在一份拷贝，并且不会在子类中有一份拷贝存在，子类中调用这个属性值访问的也是父类那个域的值。如，（**static方法不具有多态性，存在父类的常量池中**）：  
![](img/3.png)  
![](img/4.png)

##内部类（用途和麻烦）：##
###获取当前内部类对象所链接的外围类对象的引用###
在内部类中的方法内部，调用外围类类名.this方法会返回当前内部类所连接的外围类对象的引用，（内部类如果使用了外部环境的状态，那么，内部类加上创建它的外部环境，就叫做闭包）如：

```java
public class EnclosingClass {

    private int i = 0;

    class InnerClass {
        public EnclosingClass getEnclosingClass() {
            EnclosingClass.this.i = 2;
            return EnclosingClass.this;
        }
    }

}
```

###什么时候会用到内部类？###
隐藏某些实现、多继承、单元测试、闭包问题（即如果一个类继承了某个父类，这个类还想实现一个接口，但是父类和这接口有些方法或属性有冲突，想把父类和接口的功能都保留下来，那么，就可以用内部类来配合，用接口加内部类来实现闭包）

###继承内部类###
继承自内部类时有点麻烦（语法很怪！！！），使用默认的构造器会报错，因为内部类会默认的获得指向其外部类对象的引用，所以继承内部类时应该在构造器参数中传递一个其外部类对象的引用（编译器促使你一定要这样），然后在构造器中使用该外部类对象引用的super方法（该super方法调用的是这个外部类对象的内部类的构造方法）。如果父类和接口都有一个方法，他们的方法签名相同，那么子类中的这个方法，既是父类方法的重写又是接口方法的实现。如，

![](img/6.jpg) 
![](img/7.jpg)

内部类的构造器和其他方法都会默认传递一个外围类对象做参数，如：

![](img/8.png)

去掉这个内部类的无参构造器时，则用反射获取不到其构造器（即，不显示的定义内部类构造器，使用反射就获取不到内部类的构造器【有参无参均获取不到】），显示的定义一个无参构造器，则可以获取到使用了外部类对象当做其默认参数的内部类构造器。

##异常##
异常的问题？异常在有的情况下会被忽略！如（直接在finally中抛出新异常或者在finally中使用return）：  

![](img/9.png)

而且，子类抛出的异常会有限制，子类可以：

1. 不抛出异常；
2. 抛出父类异常说明中的异常或这些异常的子类；
3. 抛出未受检验的异常（unchecked exception）。

子类直接抛出的异常（方法名后面的那些throws）不能比父类更宽泛，但是可以在catch中抛出更宽泛的异常。

##正则表达式##
Pattern类和Matcher类的使用方法：

- 一般使用：

1. 首先，调用Pattern的静态方法compile(regex)把正则表达式编译成Pattern对象。另一个静态方法compile(regex, flag)则接受一个标记：COMMENTS(?x)忽略正则表达式中的空格和#后面的注释；CASE_INSENSITIVE(?i)忽略大小写；MULTILINE(?m)使得^和$匹配每行的开头和结尾，而不是整个输入串的开头和结尾；DOTALL(?s)使得.能匹配所有字符包括行终结符。
2. 其次，在该编译好的pattern对象上调用matcher(string)方法，生成一个Marcher对象。
3. 然后，字符串和正则表达式都已准备好，就可以在matcher上面调用各种方法进行操作了。

- 方法熟悉：

1. Pattern的静态方法matches(regex, string)，判断正则表达式是否能匹配字符串，返回boolean。相当于matcher对象的无参方法matches()。
2. Matcher对象的方法：无参方法<font color="red">lookingAt()</font>，匹配字符串的起始部分，如果返回true，则可以接着调用group方法获得匹配了的字符串部分；无参<font color="red">find()</font>，寻找字符串的下一个匹配，返回true之后，可以调用group、start（包含）和end（不包含）方法操作；有参<font color="red">find(index)</font>，相当于从第index位置起的无参find()；无参<font color="red">group()</font>，在find()操作之后，因为要先用find找到匹配，才能返回匹配的部分，group返回匹配了的string，和start()、end()可以一起用，来获得匹配部分的详细信息。无参<font color="red">reset()</font>，在find()迭代完成之后，调用reset重置，可以重新迭代。有参<font color="red">reset(string)</font>，则表示把matcher作用于新的string，即参数；<font color="red">appendReplacement(StringBuffer, replacement)</font>【把matcher上匹配到的结果替换为replacement，replacement中可以使用组号获取正则表达式中的组，然后再把替换后的结果挂载到StringBuffer中】，允许在替换的时候做一些特殊处理，一步一步进行替换，把上一次匹配和这次匹配之间的结果（包括这次匹配替换）挂在到stringbuffer上去，<font color="red">appendTail(stringbuffer)</font>把最后一次匹配之后剩余的字符串挂载到stringbuffer上。如，  
![](img/10.png)

###[]和()的区别###
[]表示字符类，一般表示匹配[]里面的一个字符，比如[^abc]，表示除abc外的其他一个任意字符。注：^放在中括号中才表示“非”的意思。()表示捕获组，比如，想要问号作用与前面的所有范围，则用(abc)?而不是abc?。

###量词匹配的贪婪型、勉强型和占有型###
贪婪型属于正常的表示（平时写的那些），勉强型则在后面加个问号，占有型加个加号，都只作用于前面的问号、星号、加号、大括号，因为前面如果没有这些，就变成普通的问号和加号了（也就是变成贪婪型了）。

- 贪婪型的匹配原理，一个一个匹配，先一直匹配到最后，发现最后的字符不匹配时，往前退一格再匹配，不匹配时再退一格，递归；
- 勉强型是匹配到一个字符后看看匹配能否结束，能结束就结束；
- 占有型（完全匹配）是从第一个匹配开始，把后面所有字符串读入来匹配，一直匹配到最后，如果最后的字符不匹配的话，那么也不回退，返回false结束。如，  
![](img/11.png)

第三个例子的量词是占有型，所以在寻找匹配时失败。在这种情况下，整个输入的字符串被.*+消耗了，什么都没有剩下来满足表达式末尾的“foo”。

第一次学习正则和string的时候做了笔记要多用scanner，因为scanner可以和正则表达式配合着分词（设定一个delimiter，默认是空格分词）、取得匹配的string（取数据时传入regex，默认取得空格分开的string）、解析数据（各种nextInt、nextFloat方法）。如：  
![](img/12.png)

##RTTI和反射##
一直的疑惑，能不能自动找出一个类的所有子类？这个是无法实现的。最好的方法就是维护一个数组或list，每创建一个类就把这个类的信息（Class对象或者类名或该类的对象）放进去，然后扫描这个数组或list就可以得到所有子类实现了。最好的实现就是使用工厂方法模式，每个类不用构造器去创建对象而是使用静态的工厂方法：首先创建一个工厂接口（可以维护一个static的list），包含一个静态的工厂方法，然后创建工厂实现该接口。每创建一个类（对应一个工厂类）的同时，往接口的list手动添加该类的信息，则可以扫描到所有子类。

**Thinking in java中的一个错误（是作者犯得错误还是编译器版本不同造成的）？**利用反射，可以修改final域的基本类型的值，在eclipse中不能修改final域的String对象，【但是用文本编辑器，使用javac编译，则可以修改final域的对象（String也可以）】。但是在两种情况下，都不能修改static final域。如，

1. final域类（没有static修饰符，如果有static修饰符，试图修改static final域的值，则会在运行时抛出IllegalAccessException异常）  
![](img/13.png)
2. 利用反射获取和修改final域（用sublime编辑，javac编译的情况）  
![](img/14.png)
3. 输出  
![](img/15.png)

###结论：###
只要知道方法名，只要知道变量名，利用反射就可以随意获取一个类的信息，调用一个类的方法(method.invoke(obj))，无论访问权限修饰符是什么！（Method和Field都有setAccessible(boolean)方法，可以把访问权限设置为public【但是获取修饰符时，private修改访问权限之后不会显示为public】）【class.getMethods()会获取继承而来的所有方法，class.getDeclaredMethods()获取类中声明的方法】  
![](img/16.png)


动态代理是动态地创建代理并动态地处理对所代理方法的调用。实现动态代理需要实现InvocationHandler接口，实现其invoke(object, method, args[])函数，传递的是一个代理实例（通常不管（Proxy类库的$Proxy0），参见[http://paddy-w.iteye.com/blog/841798](http://paddy-w.iteye.com/blog/841798)），方法，和参数。动态代理对象是用静态方法Proxy.newProxyInstance()方法创建的，第一个参数是希望代理的接口的类加载器，第二个参数是希望该代理实现的接口列表（Class对象数组），第三个参数是InvocationHandler接口的一个实现。动态代理代理的方法都会经过第三个参数的对象所实现的invoke方法来进行代理调用，因此通常会向调用处理器传递一个“实际对象”的引用（如下面的readObject对象），从而使得调用处理器可以将请求转发。  
![](img/17.png)  
其中，  
代理类实例proxy的类名是：$Proxy0  
proxy中的属性有：m1, m0, m3, m4, m2,  
proxy中的方法有：equals, toString, hashCode, doSomething, somethingElse,  
proxy的父类是：class java.lang.reflect.Proxy,  
proxy实现的接口是：opensource.Test$Interface.

###动态代理的作用：###
主要用来做方法的增强，让你可以在不修改源码的情况下，增强一些方法，在方法执行前后做任何你想做的事情（甚至根本不去执行这个方法），因为在InvocationHandler的invoke方法中，你可以直接获取正在调用方法对应的Method对象，具体应用的话，比如可以**添加调用日志，做事务控制**等。还有一个有趣的作用是可以用作远程调用，比如现在有Java接口，这个接口的实现部署在其它服务器上，在编写客户端代码的时候，没办法直接调用接口方法，因为接口是不能直接生成对象的，这个时候就可以考虑代理模式（动态代理）了，通过Proxy.newProxyInstance代理一个该接口对应的InvocationHandler对象，然后在InvocationHandler的invoke方法内封装通讯细节就可以了。具体的应用，最经典的当然是Java标准库的RMI，其它比如hessian，各种webservice框架中的远程调用，大致都是这么实现的。

##泛型##
容器类泛型尖括号表示的是想持有什么样的类型，比如List\<String\> list = new ArrayList\<String\>();list指向的还是ArrayList的类型，只是要往其中add或get的时候是String类型的，但是Class\<Integer\> cc = Integer.class;cc = Double.class;后面这句会出错。  

以前一直理解为这里的cc指向的是Integer类型的，其实也是跟前面的list一样，这里的cc指向的是Class对象，只不过这个Class对象里面保存的是Integer的信息！

编译器会干什么，编译器不能干什么？编译器会尽力保证你放进泛型对象中的类型是正确的。编译器会检查你传进去的数据是不是正确的类型（此时不会插入任何代码，只是编译器检查），在字节码文件中，可以看到：在取出泛型对象中的数据时，编译器自动插入了一条转型代码。所以，综合来说，编译器是尽可能保证你的类型使用是安全的，但是又不能完全保证（因为运行时的类型安全是编译器保证不了的）。

###为什么不能创建泛型数组？能创建泛型对象吗？###
在泛型代码中，不能用T t = new T()形式创建对象，不能用T[] tt = new T[n]创建泛型数组，不能使用instanceof检查泛型类型。那么，

1. ***如何在泛型代码中创建对象和创建数组？***  
   解：传入类型标签，使用RTTI来创建对象和识别对象类型，创建对象和数组
2. ***创建泛型类型的数组？***  
   解：创建泛型类型的引用，指向非泛型类型的数组，然后再转型为泛型类型的数组。

![](img/18.png)  


以前理解有误，认为泛型中通配符是代表所有的类型，随意什么类型，现在需要改正一下：通配符代表的是某种确切的类型，它可以是任意的类型，但是它是确切的、确定了的。如，  
![](img/19.png)  

平时使用泛型可能会出现一个问题，因为可以向Java SE5之前的代码传递泛型容器，所以旧式代码仍旧有可能破坏容器，比如：  
![](img/20.png)  
用注释掉的那行来解决问题，即Collections的静态方法checkedList(), or checkedCollection(), checkedMap(), checkedSet(), checkedSortedMap(), checkedSortedSet(),etc. 接受想要强制类型检查的容器为第一个参数，要强制检查的类型为第二个参数。

自限定的类型的用处就是使用了自限定，就只能获得某类中泛型参数的一个版本，它将接受确切的参数类型。自限定限制只能强制作用于继承关系，如果使用自限定，就应该知道这个类所用的类型参数将与使用这个参数的类具有相同的基类型。class SuperClass\<T extends SuperClass\<T\>\>这样的基类型，在使用时只能class SubClass extends SuperClass\<SubClass\>这样，如，  
![](img/21.png)  

##数组##
以前没有注意的，数组工具类Arrays提供了很多功能的。容器类有工具类Collections，数组有Arrays。一个复制数组很好的方法是System.arraycopy()，比自己复制要快很多，基本类型数组和对象数组都可以复制，但是复制对象数组时是浅复制（shallow copy）; Arrays.equals()比较两个数组是否相等，基本类型数组的比较会自动采用包装器类型的equals方法；Arrays.sort()对数组排序，可以传入实现了Comparator接口的比较器或者数组元素自身实现Comparable接口；Arrays.binarySearch()对已经排好序的数组查找元素，若未找到，返回值是“-(应该插入的位置)-1”，如果自定义了比较器，binarySearch需要提供比较器。

##容器类的困惑##
###TreeSet中的元素保持唯一性依赖的仅仅是equals方法和hashCode方法吗？下面这个怎么解释？###
【TreeSet是基于TreeMap实现的，TreeMap的put中只使用了compareTo方法，没有用equals方法，甚至都没用hash()】  
解决：仅仅是依赖于compareTo方法，跟equals没有关系，查找的时候是从树的root进行查找，小了就往左查，大了就往右查。  
![](img/22.png)  

HashMap中，如果对keySet进行修改操作，会影响到HashMap的结果，比如，map.keySet().remove(o)，这样map中会移除o这个对象对应的那个Entry，如（HashSet就是使用HashMap来实现的），  
![](img/23.png)  

LinkedHashMap可以按照访问顺序存放entry（注意不是访问次数！），把最近访问过的元素往后放（不是总访问次数越多就越在后面），LinkedHashSet没有这功能，只有保持插入顺序。LinkedHashMap的accessOrder使用如下，  

```java
        LinkedHashMap<String, String> lhm = new LinkedHashMap<String, String>(16, 0.75f, true);
        lhm.put("2", "2");
        lhm.put("1", "1");

        lhm.get("1");
        lhm.get("1");
        lhm.get("1");
        lhm.get("2"); // 最近访问过的元素放在后面

        for (Map.Entry<String, String> entry : lhm.entrySet()) {
            System.out.println(entry.getKey() + " " + entry.getValue());
        }
        
        /** output
         *  1 1
         *  2 2
         */
```

###LinkedHashSet已经是链表，那么怎么配合哈希表工作？###
（照样当哈希表用，只不过每一项维持前后指针）LinkedHashSet的实现依赖于HashSet中的一个构造方法，该构造方法创建了一个LinkedHashMap来实现LinkedHashSet的功能（说得清楚一点就是LinkedHashSet是基于LinkedHashMap实现的），LinkedHashMap中的Entry扩展（继承）了HashMap中的Entry，HashMap中的Entry有key、value、next(Entry)、hash(int)属性，而LinkedHashMap中的Entry扩展出了before、after，所以就能实现Linked的功能，又能基本保持HashSet的性能。因为有before、after（TreeMap中有left、right、parent），所以TreeSet和LinkedHashSet的迭代一般都要比HashSet快（但是也快不了很多，效果提升不是很明显）。

HashSet和HashMap的容量自动扩充和负载因子的关系：具有允许指定负载因子的构造器，表示负载情况达到该负载因子的水平时，容量将自动增加其容量（桶位数），实现方式是使容量大致加倍，并重新将现有对象分布到新的桶位集中（称为再散列）。

以前不能理解为什么会有ConcurrentHashMap、CopyOnWriteArrayList、CopyOnWriteArraySet。现在应该知道，**<font color="red">java容器类类库采用了快速报错机制（fail-fast），会探查容器上除了你的进程所进行的操作之外的所有变化，一担它发现其他进程修改了容器，就会立刻抛出ConcurrentModificationException。所以，ConcurrentHashMap、ConcurrentLinkedQueue、CopyOnWriteArrayList、CopyOnWriteArraySet是消除了ConcurrentModificationException的。比如，CopyOnWriteArrayList的写入会导致整个底层数组复制一遍，然后在复制之后的数组上修改，修改之后再替换回去，所以不会抛出ConcurrentModificationException，锁粒度也变小了，性能比Collections.synchronizedList好，但是实时性不如后者强。但是写入操作的优先级比读取操作的优先级要高，如果对实时可见性的要求和独占访问要求不是非常严格的话，推荐使用ConcurrentHashMap、CopyOnWriteArrayList、CopyOnWriteArraySet。</font>**

###HashMap怎么根据hashCode值和桶容量来确定对象在桶内的索引的？是hashCode值和length按位与操作么？然后就得到了索引值？###
解决：无论对什么对象，HashMap都有一个方法hash(Object)，计算出这个对象的hash值，是这样计算的：  
![](img/25.png)  
然后再用indexFor(hash, table.length)找到在桶中的位置，indexFor函数中就一行代码，return hash & (length - 1); 所以，是和数据结构中学的哈希表的原理是一样的，而且，这里解决冲突用的是链地址法（double hashing是什么？），找到桶之后，再在桶的链中一个一个找(**使用链地址法来解决哈希值冲突的情况，因为可能不同的key会具有相同的哈希值（因为哈希表也就那么长））**)，如，  
![](img/26.png)  

###java.lang.ref内的Reference的子类，软引用、弱引用和虚引用。什么时候有用？###
当存在可能会耗尽内存的大对象的时候特别有用！软引用是内存敏感的，在内存不足时，垃圾回收器才会回收那些只有软引用的对象，可以用来实现高速缓存。弱引用则是在垃圾回收器工作时，只要发现了弱引用（可能不会发现），不管内存怎么样，都会回收只有弱引用的对象。虚引用在任何时候都可能被垃圾回收，对象可有可无，必须和ReferenceQueue联合使用，可以被用来在对象被清理前做一些清理前的操作。

使用BitSet而不是EnumSet的理由是：只有在运行时才知道需要多少个标志；对标志命名不合理；需要BitSet中的某种特殊的操作。

##IO##
可以从FileInputStream、FileOutputStream和RandomAccessFile中得到FileChannel，唯一与FileChannel打交道的缓冲器是ByteBuffer，所以只需要关注ByteBuffer即可。

###序列化的三种方式###
1. 实现Serializable接口（该接口没有任何方法）。使用ObjectInputStream和ObjectOutputStream，直接读取和写入对象。读取对象之后要转型。<font color="red">对对象进行还原时，不会调用对象的构造器，但是会初始化父类，调用父类的默认构造器</font>。默认的序列化不会序列化static域，需要手动实现。
2. 继承Externalizable来序列化时，需要实现writeExternal(ObjectOutput)和readExternal(ObjectInput)方法来控制序列化过程。<font color="red">恢复对象时，会初始化，会先调用默认构造器，再调用readExternal()方法</font>。
3. 在实现Serializable接口的类中添加writeObject(ObjectOutputStream)和readObject(ObjectInputStream)则可以自己定制序列化过程，相当于Externalizable的替代方法。要使用默认机制写入对象的非transient部分，则需要调用defaultWriteObject()方法。

##String.intern()在JDK6和7中的区别：##
![](img/27.png)

##java引进匿名内部类的原因：##
1. 完善多重继承
   - C++作为比较早期的面向对象编程语言，摸着石头过河，不幸的当了炮灰。比如多重继承，Java是不太欢迎继承的。因为继承耦合度太高。比如你是一个人，你想会飞，于是就继承了鸟这个类，然后你顺便拥有了一对翅膀和厚厚的羽毛，可这些玩意你并不需要。所以Java发明了接口，以契约的方式向你提供功能。想想看，你的程序里成员变量会比函数多吗？况且多重继承会遇到死亡菱形问题，就是两个父类有同样名字的函数，你继承谁的呢？其实C++也可以做到这些，那就是定义没有成员变量的纯虚类，而且所有函数都是纯虚函数。可是这些都是要靠程序员自己把握，并没有把这些功能集成到类似Interface这样的语法里。
   - 所以Java只支持单重继承，想扩展功能，去实现接口吧。很快Java的设计者就发现了他们犯了矫枉过正的错误，多重继承还是有一定用处的。比如每一个人都是同时继承父亲和母亲两个类，要不然你的身体里怎么能留着父母的血呢？Java内部类应运而生。
2. 实现事件驱动系统
   - 用来开发GUI的Java Swing使用了大量内部类，主要用来响应各种事件。Swing的工作就是在事件就绪的时候执行事件，至于事件具体怎么做，这由事件决定。这里面有两个问题：1.事件必须要用到继承 2.事件必须能访问到Swing。所以必须把事件写成内部类。
3. 闭包
   - 内部类是面向对象的闭包，因为它不仅包含创建内部类的作用域的信息，还自动拥有一个指向此外围类对象的引用，在此作用域内，内部类有权操作所有的成员，包括private成员。一般使用一个库或类时，是你主动调用人家的API，这个叫Call，有的时候这样不能满足需要，需要你注册（注入）你自己的程序（比如一个对象)，然后让人家在合适的时候来调用你，这叫Callback。
   - 当父类和实现的接口出现同名函数时，你又不想父类的函数被覆盖，回调可以帮你解决这个问题。
   - Java中匿名内部类要引用外部方法的变量时，要求变量一定要是final的，这是因为闭包机制。因为闭包会使得某些自由变量的生命周期变长，直到回调函数执行完毕。  
![](img/28.png)  
上面getHello()就是一个回调函数，它给别人注册了一个可以调用本身内部状态的接口，getHello()函数中就使用了闭包。java中每个方法在调用的时候，对方法中的参数、内部参数创建的都是局部变量，比如上图中temp传递进来，就会创建一个局部变量引用这个temp，在方法调用完毕之后这个局部变量就会被回收。<font color="red">闭包机制应该使得方法中的局部变量的生命周期延长</font>，因为该匿名内部类可以完全访问外部的状态（即getHello方法中的状态），这个被返回的匿名内部类实例也可能一直被外部引用着，如果没有使用final，方法中的状态应该会随着方法调用的结束而消亡，但是匿名内部类的实例还被外部引用着，而且这个匿名内部类的实例内部还使用了已经随着方法消亡的状态，这会造成错误。所以匿名内部类中引用着的getHello方法中的局部变量不应该随着方法调用结束而消亡。所以一定要使用final，<font color="red">使得在创建匿名内部类实例的时候，所引用的方法的局部变量被复制了一份</font>(***如何证明被复制了一份？***)，这份复制的变量的生命周期和匿名内部类的实例的生命周期是一样的，不会随着这个回调函数结束而终止。



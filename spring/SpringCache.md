##原来我们是怎么做缓存的##
这里是一个完全自定义的缓存实现，即不用任何第三方的组件来实现某种对象的内存缓存。  

场景是：对一个账号查询方法做缓存，以账号名称为 key，账号对象为 value，当以相同的账号名称查询账号的时候，直接从缓存中返回结果，否则更新缓存。账号查询服务还支持 reload 缓存（即清空缓存）。

首先定义一个实体类：账号类，具备基本的 id 和 name 属性，且具备 getter 和 setter 方法。

```java
public class Account { 
    private int id; 
    private String name; 

    public Account(String name) { 
        this.name = name; 
    }
    
    public int getId() { 
        return id; 
    }

    public void setId(int id) { 
        this.id = id; 
    }

    public String getName() { 
        return name; 
    }

    public void setName(String name) { 
        this.name = name; 
    } 
}
```

然后定义一个缓存管理器，这个管理器负责实现缓存逻辑，支持对象的增加、修改和删除，支持值对象的泛型。如下：

```java
import java.util.Map; 
import java.util.concurrent.ConcurrentHashMap; 

public class MyCacheManager<T> { 
    private Map<String,T> cache = new ConcurrentHashMap<String,T>(); 

    public T getValue(Object key) { 
        return cache.get(key); 
    } 

    public void addOrUpdateCache(String key,T value) { 
        cache.put(key, value); 
    } 

    public void evictCache(String key) {// 根据 key 来删除缓存中的一条记录
        if(cache.containsKey(key)) { 
            cache.remove(key); 
        }
    } 

    public void evictCache() {// 清空缓存中的所有记录
        cache.clear(); 
    } 
}
```

好，现在我们有了实体类和一个缓存管理器，还需要一个提供账号查询的服务类，此服务类使用缓存管理器来支持账号查询缓存，如下：  

```java
import Account; 

public class MyAccountService { 
    private MyCacheManager<Account> cacheManager; 

    public MyAccountService() { 
        cacheManager = new MyCacheManager<Account>();// 构造一个缓存管理器
    } 

    public Account getAccountByName(String acctName) { 
        Account result = cacheManager.getValue(acctName);// 首先查询缓存
        if(result!=null) { 
            System.out.println("get from cache..."+acctName); 
            return result;// 如果在缓存中，则直接返回缓存的结果
        } 
        result = getFromDB(acctName);// 否则到数据库中查询
        if(result!=null) {// 将数据库查询的结果更新到缓存中
            cacheManager.addOrUpdateCache(acctName, result); 
        } 
        return result; 
    } 

    public void reload() { 
        cacheManager.evictCache(); 
    } 

    private Account getFromDB(String acctName) { 
        System.out.println("real querying db..."+acctName); 
        return new Account(acctName); 
    } 
}
```

现在我们开始写一个测试类，用于测试刚才的缓存是否有效，如下：  

```java
public class Main { 

    public static void main(String[] args) { 
        MyAccountService s = new MyAccountService(); 
        // 开始查询账号
        s.getAccountByName("somebody");// 第一次查询，应该是数据库查询
        s.getAccountByName("somebody");// 第二次查询，应该直接从缓存返回
        s.reload();// 重置缓存
        System.out.println("after reload..."); 
        s.getAccountByName("somebody");// 应该是数据库查询
        s.getAccountByName("somebody");// 第二次查询，应该直接从缓存返回
    } 
}
```

按照分析，执行结果应该是：首先从数据库查询，然后直接返回缓存中的结果，重置缓存后，应该先从数据库查询，然后返回缓存中的结果，实际的执行结果如下：  

```
real querying db...somebody// 第一次从数据库加载
get from cache...somebody// 第二次从缓存加载
after reload...// 清空缓存
real querying db...somebody// 又从数据库加载
get from cache...somebody// 从缓存加载
```

可以看出缓存起效了，但是这种自定义的缓存方案有如下劣势：  

- 缓存代码和业务代码耦合度太高，如上面的例子，AccountService 中的 getAccountByName（）方法中有了太多缓存的逻辑，不便于维护和变更。
- 不灵活，这种缓存方案不支持按照某种条件的缓存，比如只有某种类型的账号才需要缓存，这种需求会导致代码的变更。  
- 缓存的存储这块写的比较死，不能灵活的切换为使用第三方的缓存模块

如果自己的代码中有上述代码的影子，那么你可以考虑按照下面的介绍来优化一下代码结构了，也可以说是简化。

*spring3.1以上，都支持注释驱动的缓存，spring-content.jar中包含了缓存需要的类。*

##spring缓存的Hello World##
**定义实体类、服务类和相关配置文件**  
实体类就是上面自定义缓存方案定义的 Account.java，这里重新定义了服务类，如下：  

```java
import org.springframework.cache.annotation.CacheEvict; 
import org.springframework.cache.annotation.Cacheable; 

public class AccountService { 
    @Cacheable(value="accountCache")// 使用了一个缓存名叫 accountCache 
    public Account getAccountByName(String userName) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        System.out.println("real query account."+userName); 
        return getFromDB(userName); 
    } 

    private Account getFromDB(String acctName) { 
        System.out.println("real querying db..."+acctName); 
        return new Account(acctName); 
    } 
}
```

注意，此类的 getAccountByName 方法上有一个注释 annotation，即 @Cacheable(value=”accountCache”)，这个注释的意思是，当调用这个方法的时候，会从一个名叫 accountCache 的缓存中查询，如果没有，则执行实际的方法（即查询数据库），并将执行的结果存入缓存中，否则返回缓存中的对象。这里的缓存中的 key 就是参数 userName，value 就是 Account 对象。“accountCache”缓存是在 spring*.xml 中定义的名称。

***注意：@Cacheable也可以定义类级别的缓存，放在类注解的位置，这样，每当调用该类的任意方法时，只要传入的参数相同，Spring就会使用缓存。***

@Cacheable可指定如下属性：  

- **value**：必须属性。该属性可指定多个缓存区的名字，用于指定将<font color="red">方法返回值</font>放入指定的缓存区内。
- **key**：通过SpEL表达式显式指定缓存的key。例：`#age`
- **condition**：该属性指定一个返回boolean值的SpEL表达式，只有当该表达式返回true时，Spring才会缓存方法返回值。例：`#age<18`
- **unless**：该属性指定一个返回boolean值的SpEL表达式，当该表达式返回true时，Spring就不缓存方法返回值。

***@CachePut和@Cacheable拥有相同的属性，不过@CachePut每次都是要执行方法，然后把方法返回值缓存到缓存区，不是直接从缓存区读取，即“更新”操作。***

好，因为加入了 spring，所以我们还需要一个 spring 的配置文件来支持基于注释的缓存：  

```xml
<beans xmlns="http://www.springframework.org/schema/beans" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:cache="http://www.springframework.org/schema/cache"
    xmlns:p="http://www.springframework.org/schema/p"
    xsi:schemaLocation="http://www.springframework.org/schema/beans 
        http://www.springframework.org/schema/beans/spring-beans.xsd 
        http://www.springframework.org/schema/cache 
        http://www.springframework.org/schema/cache/spring-cache.xsd"> 

    <cache:annotation-driven />

    <bean id="accountServiceBean" class="cacheOfAnno.AccountService"/> 

    <!-- generic cache manager --> 
    <bean id="cacheManager" 
        class="org.springframework.cache.support.SimpleCacheManager">
        <property name="caches"> 
            <set> 
                <bean 
                    class="org.springframework.cache.concurrent.ConcurrentMapCacheFactoryBean"
                    p:name="default" /> 

                <bean 
                    class="org.springframework.cache.concurrent.ConcurrentMapCacheFactoryBean"
                    p:name="accountCache" /> 
            </set> 
        </property> 
    </bean> 
</beans>
```

注意这个 spring 配置文件有一个关键的支持缓存的配置项：\<cache:annotation-driven />，这个配置项缺省使用了一个名字叫 cacheManager 的缓存管理器，这个缓存管理器有一个 spring 的缺省实现，即 org.springframework.cache.support.SimpleCacheManager，这个缓存管理器实现了我们刚刚自定义的缓存管理器的逻辑，它需要配置一个属性 caches，即此缓存管理器管理的缓存集合，除了缺省的名字叫 default 的缓存，我们还自定义了一个名字叫 accountCache 的缓存，使用了缺省的内存存储方案 ConcurrentMapCacheFactoryBean，它是基于 java.util.concurrent.ConcurrentHashMap 的一个内存缓存实现方案。

OK，现在我们具备了测试条件，测试代码如下：  

```java
import org.springframework.context.ApplicationContext; 
import org.springframework.context.support.ClassPathXmlApplicationContext; 

public class Main { 
    public static void main(String[] args) { 
        ApplicationContext context = new ClassPathXmlApplicationContext( 
            "spring-cache-anno.xml");// 加载 spring 配置文件

        AccountService s = (AccountService) context.getBean("accountServiceBean"); 
        // 第一次查询，应该走数据库
        System.out.print("first query..."); 
        s.getAccountByName("somebody"); 
        // 第二次查询，应该不查数据库，直接返回缓存的值
        System.out.print("second query..."); 
        s.getAccountByName("somebody"); 
        System.out.println(); 
    } 
}
```

上面的测试代码主要进行了两次查询，第一次应该会查询数据库，第二次应该返回缓存，不再查数据库，我们执行一下，看看结果：  

```
first query...real query account.somebody// 第一次查询
real querying db...somebody// 对数据库进行了查询
second query...// 第二次查询，没有打印数据库查询日志，直接返回了缓存中的结果
```

可以看出设置的基于注释的缓存起作用了，而在 AccountService.java 的代码中，我们没有看到任何的缓存逻辑代码，只有一行注释：@Cacheable(value="accountCache")，就实现了基本的缓存方案。

##如何清空缓存##
好，到目前为止，spring cache缓存程序已经运行成功了，但是还不完美，因为还缺少一个重要的缓存管理逻辑：清空缓存，当账号数据发生变更，那么必须要清空某个缓存，另外还需要定期的清空所有缓存，以保证缓存数据的可靠性。  

为了加入清空缓存的逻辑，只要对 AccountService.java 进行修改，从业务逻辑的角度上看，它有两个需要清空缓存的地方：

- 当外部调用更新了账号，则我们需要更新此账号对应的缓存
- 当外部调用说明重新加载，则我们需要清空所有缓存

```java
import org.springframework.cache.annotation.CacheEvict; 
import org.springframework.cache.annotation.Cacheable; 

public class AccountService { 
    @Cacheable(value="accountCache")// 使用了一个缓存名叫 accountCache 
    public Account getAccountByName(String userName) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        return getFromDB(userName); 
    }

    @CacheEvict(value="accountCache",key="#account.getName()")// 清空 accountCache 缓存 
    public void updateAccount(Account account) {
        updateDB(account); 
    }

    @CacheEvict(value="accountCache",allEntries=true)// 清空 accountCache 缓存
        public void reload() { 
    }

    private Account getFromDB(String acctName) { 
        System.out.println("real querying db..."+acctName); 
        return new Account(acctName); 
    }

    private void updateDB(Account account) { 
        System.out.println("real update db..."+account.getName()); 
    }
}
```

```java
import org.springframework.context.ApplicationContext; 
import org.springframework.context.support.ClassPathXmlApplicationContext; 

public class Main { 

    public static void main(String[] args) { 
        ApplicationContext context = new ClassPathXmlApplicationContext( 
        "spring-cache-anno.xml");// 加载 spring 配置文件

        AccountService s = (AccountService) context.getBean("accountServiceBean"); 
        // 第一次查询，应该走数据库
        System.out.print("first query..."); 
        s.getAccountByName("somebody"); 
        // 第二次查询，应该不查数据库，直接返回缓存的值
        System.out.print("second query..."); 
        s.getAccountByName("somebody"); 
        System.out.println(); 

        System.out.println("start testing clear cache...");    // 更新某个记录的缓存，首先构造两个账号记录，然后记录到缓存中
        Account account1 = s.getAccountByName("somebody1"); 
        Account account2 = s.getAccountByName("somebody2"); 
        // 开始更新其中一个   
        account1.setId(1212);
        s.updateAccount(account1); 
        s.getAccountByName("somebody1");// 因为被更新了，所以会查询数据库   
        s.getAccountByName("somebody2");// 没有更新过，应该走缓存   
        s.getAccountByName("somebody1");// 再次查询，应该走缓存   
        // 更新所有缓存
        s.reload(); 
        s.getAccountByName("somebody1");// 应该会查询数据库   
        s.getAccountByName("somebody2");// 应该会查询数据库   
        s.getAccountByName("somebody1");// 应该走缓存   
        s.getAccountByName("somebody2");// 应该走缓存
    }
}
```

运行结果：  

```
first query...real querying db...somebody 
second query... 
start testing clear cache... 
real querying db...somebody1 
real querying db...somebody2 
real update db...somebody1 
real querying db...somebody1 
real querying db...somebody1 
real querying db...somebody2
```

结果和期望的一致，所以，可以看出，spring cache 清空缓存的方法很简单，就是通过 @CacheEvict 注释来标记要清空缓存的方法，当这个方法被调用后，即会清空缓存。注意其中一个 @CacheEvict(value=”accountCache”, key=”#account.getName()”)，其中的 Key 是用来指定缓存的 key 的，这里因为我们保存的时候用的是 account 对象的 name 字段，所以这里还需要从参数 account 对象中获取 name 的值来作为 key，前面的 # 号代表这是一个 SpEL 表达式，此表达式可以遍历方法的参数对象，具体语法可以参考 Spring 的相关文档手册。  

@CacheEvict用于清空缓存，属性有：

- **value**：必须属性。用于指定该方法用于清除哪个缓存区的数据。
- **allEntries**：该属性指定是否清空整个缓存区。(只能填`true` or `false`)
- **beforeInvocation**：该属性指定是否在执行方法之前清除缓存。默认是在方法成功完成之后才清除缓存。(只能填`true` or `false`)
- **condition**：该属性指定一个SpEL表达式，只有当该表达式为true时才清除缓存。
- **key**：通过SpEL表达式显式指定缓存的key。

##如何按照条件操作缓存##
前面介绍的缓存方法，没有任何条件，即所有对 accountService 对象的 getAccountByName 方法的调用都会起动缓存效果，不管参数是什么值，如果有一个需求，就是只有账号名称的长度小于等于 4 的情况下，才做缓存，大于 4 的不使用缓存，那怎么实现呢？

Spring cache 提供了一个很好的方法，那就是基于 SpEL 表达式的 condition 定义，这个 condition 是 @Cacheable 注释的一个属性：  

```java
    //getAccountByName 方法修订，支持条件
    @Cacheable(value="accountCache",condition="#userName.length() <= 4")// 缓存名叫 accountCache 
    public Account getAccountByName(String userName) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        return getFromDB(userName); 
    }
```

注意其中的 condition=”#userName.length() <=4”，这里使用了 SpEL 表达式访问了参数 userName 对象的 length() 方法，条件表达式返回一个布尔值，true/false，当条件为 true，则进行缓存操作，否则直接调用方法执行的返回结果。

```java
    //测试方法
    s.getAccountByName("somebody");// 长度大于 4，不会被缓存 
    s.getAccountByName("sbd");// 长度小于 4，会被缓存
    s.getAccountByName("somebody");// 还是查询数据库
    s.getAccountByName("sbd");// 会从缓存返回
```

```
//运行结果
real querying db...somebody 
real querying db...sbd 
real querying db...somebody
```

可见对长度大于 4 的账号名 (somebody) 没有缓存，每次都查询数据库。

##多个参数进行 key 的组合##
假设 AccountService 现在有一个需求，要求根据账号名、密码和是否发送日志查询账号信息，很明显，这里需要根据账号名、密码对账号对象进行缓存，而第三个参数“是否发送日志”对缓存没有任何影响。所以，可以利用 SpEL 表达式对缓存 key 进行设计。

```java
    //Account.java (增加password属性)
    private String password; 
    
    public String getPassword() { 
        return password; 
    }

    public void setPassword(String password) { 
        this.password = password; 
    }
```

```java
    //AccountService.java（增加 getAccount 方法，支持组合 key）
    @Cacheable(value="accountCache",key="#userName.concat(#password)") 
    public Account getAccount(String userName,String password,boolean sendLog) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        return getFromDB(userName,password); 
    }
```

注意上面的 key 属性，其中引用了方法的两个参数 userName 和 password，而 sendLog 属性没有考虑，因为其对缓存没有影响。

```java
   public static void main(String[] args) { 
        ApplicationContext context = new ClassPathXmlApplicationContext( 
            "spring-cache-anno.xml");// 加载 spring 配置文件

        AccountService s = (AccountService) context.getBean("accountServiceBean"); 
        s.getAccount("somebody", "123456", true);// 应该查询数据库
        s.getAccount("somebody", "123456", true);// 应该走缓存
        s.getAccount("somebody", "123456", false);// 应该走缓存
        s.getAccount("somebody", "654321", true);// 应该查询数据库
        s.getAccount("somebody", "654321", true);// 应该走缓存
    } 
```

上述测试，是采用了相同的账号，不同的密码组合进行查询，那么一共有两种组合情况，所以针对数据库的查询应该只有两次。

```
real querying db...userName=somebody password=123456 
real querying db...userName=somebody password=654321
```

##如何做到：既要保证方法被调用，又希望结果被缓存##
根据前面的例子，我们知道，如果使用了 @Cacheable 注释，则当重复使用相同参数调用方法的时候，方法本身不会被调用执行，即方法本身被略过了，取而代之的是方法的结果直接从缓存中找到并返回了。

现实中并不总是如此，有些情况下我们希望方法一定会被调用，因为其除了返回一个结果，还做了其他事情，例如记录日志，调用接口等，这个时候，可以用 @CachePut 注释，这个注释可以确保方法被执行，同时方法的返回值也被记录到缓存中。

```java
    //AccountService.java
    @Cacheable(value="accountCache")// 使用了一个缓存名叫 accountCache 
    public Account getAccountByName(String userName) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        return getFromDB(userName); 
    }

    @CachePut(value="accountCache",key="#account.getName()")// 更新 accountCache 缓存
    public Account updateAccount(Account account) { 
        return updateDB(account); 
    }
    
    private Account updateDB(Account account) { 
        System.out.println("real updating db..."+account.getName()); 
        return account; 
    }
```

```java
    public static void main(String[] args) { 
        ApplicationContext context = new ClassPathXmlApplicationContext( 
            "spring-cache-anno.xml");// 加载 spring 配置文件

        AccountService s = (AccountService) context.getBean("accountServiceBean"); 

        Account account = s.getAccountByName("someone"); 
        account.setPassword("123"); 
        s.updateAccount(account); 
        account.setPassword("321"); 
        s.updateAccount(account); 
        account = s.getAccountByName("someone"); 
        System.out.println(account.getPassword()); 
    }
```

如上面的代码所示，我们首先用 getAccountByName 方法查询一个人 someone 的账号，这个时候会查询数据库一次，但是也记录到缓存中了。然后我们修改了密码，调用了 updateAccount 方法，这个时候会执行数据库的更新操作且记录到缓存，我们再次修改密码并调用 updateAccount 方法，然后通过 getAccountByName 方法查询，这个时候，由于缓存中已经有数据，所以不会查询数据库，而是直接返回最新的数据，所以打印的密码应该是“321”

运行结果：  

```
real querying db...someone 
real updating db...someone 
real updating db...someone 
321
```

和分析的一样，只查询了一次数据库，更新了两次数据库，最终的结果是最新的密码。说明 @CachePut 确实可以保证方法被执行，且结果一定会被缓存。

##@Cacheable、@CachePut、@CacheEvict 注释##
通过上面的例子，我们可以看到 spring cache 主要使用两个注释标签，即 @Cacheable、@CachePut 和 @CacheEvict，总结一下其作用和配置方法。

###@Cacheable###
@Cacheable: 主要针对方法配置，能够根据方法的请求参数对其结果进行缓存  

|属性|说明|补充|
|--:|:--:|---|
|value	|缓存的名称，在 spring 配置文件中定义，必须指定至少一个|例如：@Cacheable(value=“mycache”)  或者  @Cacheable(value={“cache1”, “cache2”}|
|key|缓存的 key，可以为空，如果指定要按照 SpEL 表达式编写，如果不指定，则缺省按照方法的所有参数进行组合|例如：@Cacheable(value=“testcache”, key=“#userName”)|
|condition|缓存的条件，可以为空，使用 SpEL 编写，返回 true 或者 false，只有为 true 才进行缓存|例如：@Cacheable(value=“testcache”, condition=“#userName.length()>2”)|
|unless|（与condition含义刚好相反）|（略）|

###@CachePut###
@CachePut: 主要针对方法配置，能够根据方法的请求参数对其结果进行缓存，和 @Cacheable 不同的是，它每次都会触发真实方法的调用

|属性|说明|补充|
|--:|:--:|---|
|value	|缓存的名称，在 spring 配置文件中定义，必须指定至少一个|例如：@CachePut(value=“mycache”)  或者 @CachePut(value={“cache1”, “cache2”}|
|key|缓存的 key，可以为空，如果指定要按照 SpEL 表达式编写，如果不指定，则缺省按照方法的所有参数进行组合|例如：@CachePut(value=“testcache”, key=“#userName”)|
|condition|缓存的条件，可以为空，使用 SpEL 编写，返回 true 或者 false，只有为 true 才进行缓存|例如：@CachePut(value=“testcache”, condition=“#userName.length()>2”)|
|unless|（与condition含义刚好相反）|（略）|

###@CacheEvict###
@CacheEvict: 主要针对方法配置，能够根据一定的条件对缓存进行清空

|属性|说明|补充|
|--:|:--:|---|
|value|缓存的名称，在 spring 配置文件中定义，必须指定至少一个|例如： @CacheEvict(value=“mycache”) 或者 @CacheEvict(value={“cache1”, “cache2”}|
|key|缓存的 key，可以为空，如果指定要按照 SpEL 表达式编写，如果不指定，则缺省按照方法的所有参数进行组合|例如： @CacheEvict(value=“testcache”, key=“#userName”)|
|condition|缓存的条件，可以为空，使用 SpEL 编写，返回 true 或者 false，只有为 true 才清空缓存|例如： @CacheEvict(value=“testcache”, condition=“#userName.length()>2”)|
|allEntries|是否清空所有缓存内容，缺省为 false，如果指定为 true，则方法调用后将立即清空所有缓存|例如： @CacheEvict(value=“testcache”, allEntries=true)|
|beforeInvocation|是否在方法执行前就清空，缺省为 false，如果指定为 true，则在方法还没有执行的时候就清空缓存，缺省情况下，**如果方法执行抛出异常，则不会清空缓存**|例如：@CacheEvict(value=“testcache”，beforeInvocation=true)|

##扩展性##
直到现在，我们已经学会了如何使用开箱即用的 spring cache，这基本能够满足一般应用对缓存的需求，但现实总是很复杂，当你的用户量上去或者性能跟不上，总需要进行扩展，这个时候你或许对其提供的内存缓存不满意了，因为其不支持高可用性，也不具备持久化数据能力，这个时候，你就需要自定义你的缓存方案了，还好，spring 也想到了这一点。

我们先不考虑如何持久化缓存，毕竟这种第三方的实现方案很多，我们要考虑的是，怎么利用 spring 提供的扩展点实现我们自己的缓存，且在不改原来已有代码的情况下进行扩展。

首先，我们需要提供一个 CacheManager 接口的实现，这个接口告诉 spring 有哪些 cache 实例，spring 会根据 cache 的名字查找 cache 的实例。另外还需要自己实现 Cache 接口，Cache 接口负责实际的缓存逻辑，例如增加键值对、存储、查询和清空等。利用 Cache 接口，我们可以对接任何第三方的缓存系统，例如 EHCache、OSCache，甚至一些内存数据库例如 memcache 或者 h2db 等。

```java
import java.util.Collection; 
import org.springframework.cache.support.AbstractCacheManager; 

public class MyCacheManager extends AbstractCacheManager { 
    private Collection<? extends MyCache> caches; 

    /** 
    * Specify the collection of Cache instances to use for this CacheManager. 
    */ 
    public void setCaches(Collection<? extends MyCache> caches) { 
        this.caches = caches; 
    }

    @Override 
    protected Collection<? extends MyCache> loadCaches() { 
        return this.caches; 
    }
}
```

上面的自定义的 CacheManager 实际继承了 spring 内置的 AbstractCacheManager，实际上仅仅管理 MyCache 类的实例。

```java
import java.util.HashMap; 
import java.util.Map; 

import org.springframework.cache.Cache; 
import org.springframework.cache.support.SimpleValueWrapper; 

public class MyCache implements Cache { 
    private String name; 
    private Map<String,Account> store = new HashMap<String,Account>();; 

    public MyCache() { 
    } 

    public MyCache(String name) { 
        this.name = name; 
    } 

    @Override 
    public String getName() { 
        return name; 
    } 

    public void setName(String name) { 
        this.name = name; 
    } 

    @Override 
    public Object getNativeCache() { 
        return store; 
    } 

    @Override 
    public ValueWrapper get(Object key) { 
        ValueWrapper result = null; 
        Account thevalue = store.get(key); 
        if(thevalue!=null) { 
            thevalue.setPassword("from mycache:"+name); 
            result = new SimpleValueWrapper(thevalue); 
        } 
        return result; 
    } 

    @Override 
    public void put(Object key, Object value) { 
        Account thevalue = (Account)value; 
        store.put((String)key, thevalue); 
    } 

    @Override 
    public void evict(Object key) { 
    } 

    @Override 
    public void clear() { 
    }
}
```


上面的自定义缓存只实现了很简单的逻辑，但这是我们自己做的，也很令人激动是不是，主要看 get 和 put 方法，其中的 get 方法留了一个后门，即所有的从缓存查询返回的对象都将其 password 字段设置为一个特殊的值，这样我们等下就能演示“我们的缓存确实在起作用！”了。
这还不够，spring 还不知道我们写了这些东西，需要通过 spring*.xml 配置文件告诉它。

```xml
<beans xmlns="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:cache="http://www.springframework.org/schema/cache"
    xmlns:p="http://www.springframework.org/schema/p"  
    xsi:schemaLocation="http://www.springframework.org/schema/beans 
        http://www.springframework.org/schema/beans/spring-beans.xsd 
        http://www.springframework.org/schema/cache 
        http://www.springframework.org/schema/cache/spring-cache.xsd"> 

    <cache:annotation-driven /> 

    <bean id="accountServiceBean" class="cacheOfAnno.AccountService"/> 

    <!-- generic cache manager --> 
    <bean id="cacheManager" class="cacheOfAnno.MyCacheManager">
        <property name="caches"> 
            <set> 
                <bean 
                  class="cacheOfAnno.MyCache"
                  p:name="accountCache" /> 
            </set> 
        </property> 
    </bean> 
</beans>
```

```java
public static void main(String[] args) { 
    ApplicationContext context = new ClassPathXmlApplicationContext( 
        "spring-cache-anno.xml");// 加载 spring 配置文件

    AccountService s = (AccountService) context.getBean("accountServiceBean"); 

    Account account = s.getAccountByName("someone"); 
    System.out.println("passwd="+account.getPassword()); 
    account = s.getAccountByName("someone"); 
    System.out.println("passwd="+account.getPassword()); 
}
```

上面的测试代码主要是先调用 getAccountByName 进行一次查询，这会调用数据库查询，然后缓存到 mycache 中，然后我打印密码，应该是空的；下面我再次查询 someone 的账号，这个时候会从 mycache 中返回缓存的实例，记得上面的后门么？我们修改了密码，所以这个时候打印的密码应该是一个特殊的值。

运行结果：  

```
real querying db...someone 
passwd=null 
passwd=from mycache:accountCache
```

结果符合预期，即第一次查询数据库，且密码为空，第二次打印了一个特殊的密码。说明 myCache 起作用了。

##注意和限制##
###基于 proxy 的 spring aop 带来的内部调用问题###
上面介绍过 spring cache 的原理，即它是基于动态生成的 proxy 代理机制来对方法的调用进行切面，这里关键点是对象的引用问题，如果对象的方法是内部调用（即 this 引用）而不是外部引用，则会导致 proxy 失效，那么我们的切面就失效，也就是说上面定义的各种注释包括 @Cacheable、@CachePut 和 @CacheEvict 都会失效。

```java
    public Account getAccountByName2(String userName) { 
        return this.getAccountByName(userName); 
    } 

    @Cacheable(value="accountCache")// 使用了一个缓存名叫 accountCache 
    public Account getAccountByName(String userName) { 
        // 方法内部实现不考虑缓存逻辑，直接实现业务
        return getFromDB(userName); 
    }
```

上面我们定义了一个新的方法 getAccountByName2，其自身调用了 getAccountByName 方法，这个时候，发生的是内部调用（this），所以没有走 proxy，导致 spring cache 失效。

```java
    public static void main(String[] args) { 
    ApplicationContext context = new ClassPathXmlApplicationContext( 
        "spring-cache-anno.xml");// 加载 spring 配置文件

    AccountService s = (AccountService) context.getBean("accountServiceBean"); 

    s.getAccountByName2("someone"); 
    s.getAccountByName2("someone"); 
    s.getAccountByName2("someone"); 
}
```

运行结果：

```
real querying db...someone 
real querying db...someone 
real querying db...someone
```

可见，结果是每次都查询数据库，缓存没起作用。要避免这个问题，就是要避免对缓存方法的内部调用，或者避免使用基于 proxy 的 AOP 模式，可以使用基于 aspectJ 的 AOP 模式来解决这个问题。

###Reference:###
[1] [http://www.ibm.com/developerworks/cn/opensource/os-cn-spring-cache/index.html](http://www.ibm.com/developerworks/cn/opensource/os-cn-spring-cache/index.html)


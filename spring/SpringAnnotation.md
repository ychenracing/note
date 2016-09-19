```java
// @RequestMapping(value = "/page/{id}", method = RequestMethod.GET)
// @RequestParam(value = "serviceId", required = false)
// @PathVariable(value = "name")
// @RequestHeader(value = "Keep-Alive")
// @CookieValue(value = "JSESSIONID")
// @SessionAttributes("loginUser") 只要该controller下面的方法执行model.addAttribute("loginUser","jadyer")
// 那么"loginUser"便被自动放到HttpSession  
// @ModelAttribute
// @ResponseBody
// @Scope("prototype") || @Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
// @Qualifer("userServiceImpl")
// @Resource(name = "", type = *.class)
// @PostConstruct
// @PreDestory

import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.SessionAttributes;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import org.springframework.web.servlet.view.InternalResourceViewResolver;

/**
 * UserController
 * @author http://blog.csdn.net/jadyer
 * @create Apr 20, 2012 1:23:29 AM
 */
@Controller //指明这是一个Controller
@RequestMapping(value="/mydemo") //类似于命名空间，即访问该Controller时必须加上"/mydemo"在前面
//只要下面的方法中执行model.addAttribute("loginUser","jadyer")那么"loginUser"便被自动放到HttpSession
@SessionAttributes("loginUser")
public class UserController {

    @Autowired // @Resource(name = "", type = UserController.class) @Autowired默认使用类型来自动装备，@Resource默认使用Bean的名称来自动装配
    @Qualifier("userServiceImpl") 配合@Autowired，可以使用Bean的名称来自动装配，可以用于创建Bean和装配Bean的地方
    public IUserService userService;  

    /**
     * @see 如果在类上指定@RequestMapping并给了值，而在方法上指定@RequestMapping但不给值
     * @see 这时，以下的两种请求方式，都会被分发到该方法上
     * @see 第一种:'http://127.0.0.1:8088/SpringMVC_study/mydemo'
     * @see 第二种:'http://127.0.0.1:8088/SpringMVC_study/mydemo/'
     * @see 但，如果我们在某个方法上明确指定了@RequestMapping(value="/")，则第二种请求会被分发到该方法上
     */
    @RequestMapping
    public String login(){
        System.out.println("login() is invoked");
        return "addSuccess";
    }
    
    @RequestMapping(value={"/","/add"}) //即访问"/mydemo/"或者"/mydemo/add"，便自动访问该方法
    public String addUser(){
        System.out.println("addUser() is invoked");
        return "addSuccess"; //return逻辑视图
    }
    
    /**
     * 简述如何接收前台参数，以及@RequestParam的使用
     */
    //这里@RequestParam("userID")表明在访问该方法时，必须传个参数过来，并且参数名必须是int型的userID
    //以下三种情况会导致服务器返回HTTP Status 400
    //1)没有传任何参数2)传的参数中没有名为userID的参数3)传了userID参数但其参数值无法转换为int型
    @RequestMapping(value={"/delete"})
    public String deleteUser(@RequestParam("userID") int userID){
        System.out.println("===============" + userID);
        return "addSuccess";
    }
    //这里@RequestParam表明在访问该方法时，至少要把userName参数传过来，否则服务器返回HTTP Status 400
    @RequestMapping("/edit")
    public String editUser(@RequestParam String userName){
        System.out.println("===============" + userName);
        return "addSuccess";
    }
    //这种情况下，无论传不传userName参数，都可以访问到该方法。如果没有传userName，则打印出来的值就是null
    //这里method=RequestMethod.GET用于指定需要以GET方式访问该方法，注意两个以上属性时就要明确value值了
    @RequestMapping(value="/modify", method=RequestMethod.GET)
    public String modifyUser(String userName){
        System.out.println("===============" + userName);
        return "addSuccess";
    }
    
    /**
     * 简述如何返回参数给前台，以及前台如何获取参数
     */
    @RequestMapping("/sayaaa")
    public String sayAaa(String userName, Map<String,Object> map){
        map.put("aaa_name", "aaa_jadyer"); //此时前台使用${aaa_name}即可取值
        return "addSuccess";
    }
    @RequestMapping("/saybbb")
    public String sayBbb(String userName, Model model){
        model.addAttribute("bbb_name", "bbb_jadyer"); //此时前台使用${bbb_name}即可取值
        model.addAttribute("loginUser","jadyer"); //由于@SessionAttributes，故loginUser会被自动放到HttpSession中
        return "addSuccess";
    }
    @RequestMapping("/sayccc")
    public String sayCcc(String userName, Model model){
        model.addAttribute("ccc_jadyer"); //此时默认以Object类型作为key，即String-->string，故前台使用${string}即可取值
        return "addSuccess";
    }

    /** 
     * 测试返回JSON数据 
     * @param session 
     * @return 
     */  
    @RequestMapping(value="/test")  
    @ResponseBody  
    public Object test(HttpSession session){ 
        System.out.println("test....................");  
        return session.getAttribute("permit");  
    } 
    
    /**
     * 简述如何获取javax.servlet.http.HttpServletRequest、HttpServletResponse、HttpSession
     */
    @RequestMapping("/eat")
    public String eat(HttpServletRequest request, HttpServletResponse response, HttpSession session){
        System.out.println("===============" + request.getParameter("myname"));
        System.out.println("===============" + request.getLocalAddr());
        System.out.println("===============" + response.getLocale());
        System.out.println("===============" + session.getId());
        return "addSuccess";
    }
    
    /**
     * 简述客户端跳转时,传参的传递
     * @see 注意:这种情况下的参数，并不是放到HttpSession中的，不信你可以试一下
     * @see 注意:即先访问/mydemo/sleep之后，再直接访问/mydemo/eat
     */
    @RequestMapping("/sleep")
    public String sleep(RedirectAttributes ra){
        ra.addFlashAttribute("redirectName", "redirectValue");
        //等同于return "redirect:/mydemo/eat"; //两种写法都要写绝对路径,而SpringMVC都会为其自动添加应用上下文
        return InternalResourceViewResolver.REDIRECT_URL_PREFIX + "/mydemo/eat";
    }
}
```


##Spring 后处理器/Bean 生命周期##
###BeanPostProcessor###
bean后处理器，对容器中的bean进行后处理增强。
实现BeanPostProcessor即可，Spring会在每次创建该bean的时候，进行bean后处理增强。  

- postProcessBeforeInitialization(Object bean, String beanName)会对bean初始化之前进行后处理增强，参数bean即是被增强的bean，beanName是bean的id。  
- postProcessAfterInitialization(Object bean, String beanName)会对bean初始化之后进行后处理增强，参数bean即是被增强的bean，beanName是bean的id。

被增强处理的Bean类还可实现InitializingBean接口，实现其afterPropertiesSet()方法。

然后在spring配置文件中注册该BeanPostProcessor实现即可，spring会自动注册和采用该Bean后处理器。

然后调用的先后关系（**Spring Bean的生命周期**）：  


1. 先Spring创建Bean，分配存储空间，调用该Bean的构造器，实例化。
2. 注入依赖。Spring注入Bean的属性。
3. 如果该Bean实现了BeanNameAware接口，调用BeanNameAware的setBeanName方法。
4. 如果该Bean实现了BeanFactoryAware接口，调用BeanFactoryAware的setBeanFactory方法。
5. 调用BeanPostProcessor的postProcessBeforeInitialization()方法。
6. 调用该Bean实现了InitializingBean接口，则调用InitializingBean的afterPropertiesSet()方法。
7. 如果定义该Bean时指定了init-method，则执行该初始化方法（init-method，不是构造器）。
8. 调用BeanPostProcessor的postProcessAfterInitialization()方法。
9. 该Bean可以使用了。Spring在这个时候会把Bean注入到想要使用该Bean的地方。
10. 容器关闭时，如果该Bean实现了DisposableBean接口，则调用DisposableBean的destory()方法。
11. 如果定义该Bean时指定了destory-method，则执行该销毁方法。


```shell
现在开始初始化容器
九月 19, 2016 5:51:18 下午 org.springframework.context.support.ClassPathXmlApplicationContext prepareRefresh
信息: Refreshing org.springframework.context.support.ClassPathXmlApplicationContext@4b85612c: startup date [Mon Sep 19 17:51:18 CST 2016]; root of context hierarchy
九月 19, 2016 5:51:18 下午 org.springframework.beans.factory.xml.XmlBeanDefinitionReader loadBeanDefinitions
信息: Loading XML bean definitions from class path resource [com/iqiyi/yorkchen/beanlifecycle/beanlifecycle.xml]
这是BeanFactoryPostProcessor实现类构造器！！
BeanFactoryPostProcessor调用postProcessBeanFactory方法，phone属性改为18317137813
这是BeanPostProcessor实现类构造器！！
这是InstantiationAwareBeanPostProcessorAdapter实现类构造器！！
InstantiationAwareBeanPostProcessor调用postProcessBeforeInstantiation方法
【构造器】调用Person的构造器
InstantiationAwareBeanPostProcessor调用postProcessAfterInstantiation方法
InstantiationAwareBeanPostProcessor调用postProcessPropertyValues方法
【注入属性】注入Person的属性address
【注入属性】注入Person的属性name
【注入属性】注入Person的属性phone
【BeanNameAware接口】调用BeanNameAware.setBeanName()
【BeanFactoryAware接口】调用BeanFactoryAware.setBeanFactory()
BeanPostProcessor接口方法postProcessBeforeInitialization对属性进行更改！
InstantiationAwareBeanPostProcessor调用postProcessBeforeInitialization方法
【init-method】调用<bean>的init-method属性指定的初始化方法
【InitializingBean接口】调用InitializingBean.afterPropertiesSet()
BeanPostProcessor接口方法postProcessAfterInitialization对属性进行更改！
InstantiationAwareBeanPostProcessor调用postProcessAfterInitialization方法
容器初始化成功
Person [name=陈勇, address=上海, phone=18317137813]
现在开始关闭容器！
九月 19, 2016 5:51:18 下午 org.springframework.context.support.ClassPathXmlApplicationContext doClose
信息: Closing org.springframework.context.support.ClassPathXmlApplicationContext@4b85612c: startup date [Mon Sep 19 17:51:18 CST 2016]; root of context hierarchy
【destroy-method】调用<bean>的destroy-method属性指定的初始化方法
【DiposibleBean接口】调用DiposibleBean.destory()

```

**用处**  
增强处理，生成proxy。

###BeanFactoryPostProcessor###
对Spring容器进行增强处理。Spring对该BeanFactoryPostProcessor的回调比BeanPostProcessor要早，可以使用该BeanFactoryPostProcessor获取BeanDefinition并对Bean进行修改。

##Spring整合Mybatis##
MyBatis整合Spring最简单的理解就是***把MyBatis数据源的配置、事务的管理、SqlSessionFactory的创建以及数据映射器接口Mapper的创建交由Spring去管理***，所以MyBatis的配置文件mybatis-config.xml中不需要再配置数据源及事务，在业务层Service实现时不需要手动地获取SqlSession以及对应的数据映射器接口Mapper，通过Spring的注入即可。

然而，使用MyBatis注解可以直接省略mybatis-config.xml配置。例如，

- 首先，定义一个注解。注解用来标识dao接口：   

``` java
import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

import org.springframework.stereotype.Component;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@Documented
@Component
public @interface MyBatisDao {
    String value() default "";
}
```   
- 在Spring的配置文件中配置MapperScannerConfigurer：

```xml
	<!--把mybatis SqlSessionFactory的创建交由spring管理 -->
	<bean id="sqlsessionfactorybean" class="org.mybatis.spring.SqlSessionFactoryBean">
		<property name="dataSource" ref="mydatasource"></property>
		<property name="mapperLocations" value="classpath:cn/edu/fudan/iipl/mapper/*.xml"></property>
	</bean>

	<!-- DAO接口所在包名，Spring会自动查找其下用MyBatisDao注解的类 -->
	<bean id="mapperscannerconfigurer" class="org.mybatis.spring.mapper.MapperScannerConfigurer">
		<property name="basePackage" value="cn.edu.fudan.iipl"></property>
		<property name="annotationClass" value="cn.edu.fudan.iipl.annotation.MyBatisDao"></property>
		<property name="sqlSessionFactoryBeanName" value="sqlsessionfactorybean"></property>
	</bean>
```

然后，用注解@MyBatisDao标注在dao接口上即可，mybatis会把该接口与mapper对应起来。

如果想启用spring的事务，可以使用：

```xml
	<!--把mybatis的事务交由spring去管理 -->
	<bean id="transactionManager"
		class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
		<property name="dataSource" ref="mydatasource" /><!--注意：此处的数据源要与sqlSessionFactory中的dataSource相同 -->
	</bean>

	<!--启用spring @Transactional注解 -->
	<tx:annotation-driven />
```

##一级缓存与二级缓存##
mybatis一级缓存是指同一个session的方法，第一次与数据库交互，第二次使用缓存，不同session则都是每个session的第一次都是与数据库交互。二级缓存是指不同session，只要调用的方法、参数相同，那么就是总的第一次交互数据库，第二次使用缓存。

mybatis开启二级缓存：

- 在mapper文件中写上： 

```xml
<cache eviction="LRU" size="1024" readOnly="true"></cache>
```

- 在select、update、insert、delete等语句上写上：

```xml
	<select id="getAll" resultMap="articleMap" flushCache="false"
		useCache="true">
		select * from article
	</select>
	
	<update id="updateArticle" parameterType="cn.edu.fudan.iipl.entity.Article"
		flushCache="true">
		update article set
		title=#{title},mainbody=#{mainBody},category=#{category},author=#{author},gmt_modify=#{gmtModify}
		where id=#{id}
	</update>
	
	<insert id="addArticle" parameterType="cn.edu.fudan.iipl.entity.Article"
		useGeneratedKeys="true" keyProperty="id" flushCache="true">
		insert into
		article(title,mainbody,category,author,gmt_create,gmt_modify)
		values(#{title},#{mainBody},#{category},#{author},#{gmtCreate},#{gmtModify})
	</insert>

	<delete id="deleteById" parameterType="int" flushCache="true">
		delete
		from article where id=#{id}
	</delete>
```

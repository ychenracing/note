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
// @Scope("prototype")
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

    @Autowired // @Resource(name = "", type = UserController.class)
    @Qualifier("userServiceImpl")         
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
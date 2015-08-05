我们在工作中会听到很多关于测试的名词，如单元测试UT，集成测试`Integration Test`，端到端测试`end-to-end`等等。

我认为，大部分人其实都仅仅是有一个模糊的认识。他们并未真正清楚每种测试的含义。

当领导强调要做xx测试时，就随意的把概念扔给下属，其实自己都不清楚为什么要做，怎么做。

而据我所知，国内大部分公司更是糟糕。每个开发人员都完全投入到写代码中，甚至不愿意花时间写最最最基本的单元测试。

同时测试的重要性已经不仅仅是对质量的保证了。在流行敏捷开发的今天，测试已经成为敏捷开发的重要组成部分。

因此我们是否真的明白测试的含义。它们的必要性，应该如何定义它们，它们之间有严格的界限吗，每种测试类型适合的工具是什么。

这些都是我们必须思考的问题。

##单元测试 Unit Test##

###单元测试的定义：###
A unit test is a test written by the programmer to verify that a relatively small piece of code is doing what it is intended to do. They are narrow in scope, they should be easy to write and execute, and their effectiveness depends on what the programmer considers to be useful. The tests are intended for the use of the programmer, they are not directly useful to anybody else, though, if they do their job, testers and users downstream should benefit from seeing less bugs.

上面的定义强调了

1. UT应由开发人员写，给开发人员使用。
2. UT测试的应该是小段代码，目的是开发人员确定源代码做了希望它做的事。

再来看看TestNG的作者是如何概括UT的：

```
unit testing (testing a class in isolation of the others)
```

- 首先他强调了，一个UT case只能针对一个类。不应该在一个UT case中测试一个以上的类。
- 其次一个重点是：一个类的UT必须是完全独立的，不应再和其他部分代码有任何交互。这也是我们要使用Mockito等mock框架的原因，这样在测试代码时，当必须和其他对象交互时，就使用mock对象来保持UT的独立性。
- 此外，UT 可以是自动的，也可以是手动的。

###单元测试的工具：###
大家熟知的JUnit，以及TestNG；.net专用的NUnit；VS2010开始直接提供的测试框架。c/c++专用的CppUnit，PHP专用的PHPUnit。Mockito，easyMock等mock框架也是重要组成部分。

另外，单元测试有一个覆盖率的问题。

```
一个UT调用了被测试类中多少代码。一个不负责任的程序员写的UT也许只测试了类中的一个方法，而负责的程序员写的UT应该覆盖掉被测试类中所有主要方法。
```

Cobertura是自动检测UT覆盖率并生成报告的一个开源工具。 将这个工具集成到每天的daily build中是一种很好的做法。

要求覆盖率要达到100%是无理且无意义的，通常80~90%就行了。原因有两点：

1. 是否UT必须覆盖所有的代码？
> 让我们来看看JUnit官网的回答：  
> No, just test everything that could reasonably break.  
> 
> Be practical and maximize your testing investment. Remember that investments in testing are equal investments in design. If defects aren't being reported and your design responds well to change, then you're probably testing enough. If you're spending a lot of time fixing defects and your design is difficult to grow, you should write more tests.
> 
> If something is difficult to test, it's usually an opportunity for a design improvement. Look to improve the design so that it's easier to test, and by doing so a better design will usually emerge.

2. 对于一般项目，到达到100%的覆盖率基本不可能。  
> 尽管我们现在有各种测试框架，各种mock框架，但在很多可能的情况下都会遇到难于，甚至无法测试的代码。
> 
> 例如private方法，唯一测试的方式就是利用反射机制。
> 
> 如果测试覆盖率变成了一个目标，而不是提高代码质量，防范bug的手段，那就是本末倒置了。
> 
> 但是，如果为了方便测试而修改源代码，并不是不可理喻的行为。如果你发现代码难于测试，则有可能是代码存在一些问题。
>
> 例如，在另一篇关于Mockito的文章中提到了，为了将mock对象传递到被测试的对象中，需要源代码提供get/set方法，否则测试起来就很麻烦。
>
> 在实践中我们会慢慢发现，代码不够独立，缺乏应有的get/set方法，结构不合理，方法应该被重构等等问题，会导致难于被测试。
>
> 因此UT也是对源代码的一次review。一个有责任心的程序员，应该从UT中看到更多。永远记住一条：我们不是在为了测试而测试，我们应该思考的更多。

3. 对于每一个测试方法来说，所谓的独立到底是什么？  
> 最近遇到了关于UT的这样一个问题：每一个测试方法到底要多么“独立”？
>
> 例如，在一个被测试类中有两个方法：
> 
```java
public class app{
        public void method1(){
            String testString = method2(); //在方法一中调用了方法二。
        }
        public String method2(){
        }
}
```
>
> 于是问题是，当我们写第一个方法method1的测试方法method1Test时，我们应该mock的是什么？我们应该mock方法二？还是不需要mock？
>
> 也就是说，当我们测试方法一时，应该把方法二看做外部的东西，通过mock方法二，仅仅测试方法一。
>
> 或是不使用mock，直接调用方法一(实际同时也调用了方法二)。因此相当于同时测试了方法一和方法二的行为。
>
>
> 我本来是倾向于第一个做法，将方法一作为完全独立的被测试的部分，通过mock方法二，让方法一在被测试时，和其他类或方法完全没有关联。
>
> 但是和同事讨论以后，看法发生了变化。看起来第二种做法，同时测试了方法一和二。但是在一个类中，各个方法本来就不是完全独立的。
>
> 因此有成员变量的存在。成员变量的值天生的就可以在各个方法中传递。
>
> 因此结论是：UT的独立范围，永远是一个类。测试时，当调用了其他类的代码时，就应该使用mock将被测试类和其他类隔离开。
>
> 测试时，如果调用了同一个类的其他方法时，是不需要使用mock的。因为调用的是同一个类中的代码。


##集成测试 Integration Test##
###集成测试的定义：###
An integration test is done to demonstrate that different pieces of the system work together. Integration tests cover whole applications, and they require much more effort to put together. They usually require resources like database instances and hardware to be allocated for them. The integration tests do a more convincing job of demonstrating the system works (especially to non-programmers) than a set of unit tests can, at least to the extent the integration test environment resembles production.

因此，

1. 通常会在指定的环境运行集成测试。
2. 集成测试的目的旨在测试各个组件间是否能互相配合，正常工作。和UT一样，集成测试也是为了看代码是否按"设计或期望的方式"工作。
3. 集成测试的范围比较宽泛：范围可以小到，如果在一个UT case中涉及了多个类，就可以认为这是集成测试。大到整个系统，从后台到前端所有组件。Integration tests can be performed at the unit level or the system level.集成测试往往会涉及外部组件，如数据库，硬件，网络等等。
4. 集成测试通常应由专门的测试人员完成。

HP's (mercury) QTP or Borland's Silktest 都可以做自动化的集成测试和回归测试。

在敏捷开发的今天，一个概念变得更重要了：**CI (Continuous Integration)**

本文并不打算探讨CI，因为这又是一个很大的话题。CI 和集成测试经常结合的很紧密。

CC(CruiseContoller), 是现在常用的CI工具之一。

Hudson 是另一个较新的CI工具。[http://hudson-ci.org/](http://hudson-ci.org/)

##冒烟测试 Smoke Test##

我很喜欢这个名字，它的来源很有意思。Smoke Test是从电子硬件测试来的，表示第一次对硬件原型prototype加电时，如果硬件冒烟了，就表示产品有问题。

从smoke test名字的来由我们就可以看出，smoke test是比较初级的测试(a quick test)，仅仅是为了检查各个组件是否能一起工作，而并不去深究功能上是否正确。

A simple integration test where we just check that when the system under test is invoked it returns normally and does not blow up.

注意smoke test一般是大范围的集成测试。通常可以是整个系统/端到端的测试。

例如，一个项目：客服人员在终端上输入用户的信息，最终用户可以在互联网上查询到自己的信息。

此时的smoke test就可以是在终端上输入某个用户的信息，然后查询通过web程序是否可以找到这个用户的信息，而不必关注该用户信息的正确性。

因此有人认为它是测试的第一步：first tests on which testers can conclude if they will continue testing. 但并非是必须的。

##回归测试 Regression Test##
- A test that was written when a bug was fixed. It ensure that this specific bug will not occur again. The full name is "non-regression test".
- A regression test re-runs previous tests against the changed software to ensure that the changes made in the current software do not affect the functionality of the existing software."

上面两种观点并不一致：一种认为回归测试是为了覆盖fix的bug，另一种认为回归测试是覆盖新添加的功能。

但是我们可以看到这两种说法的统一之处：

- 回归测试是为了覆盖系统新发生的变化而进行的测试。
- 回归测试可以由测试人员编写，也可以由开发人员编写。

形式上可以就是一个覆盖新功能或者bug的UT，或者测试人员写的专用测试工具。

##端到端测试 End-To-End Test##
validates the entire application to ensure that it satisfies previously established acceptance criteria and performs as an integrated system. The purpose of system testing is not to test all possible positive and negative conditions (reserved for functional and integration testing), but to instead execute business functions and infrastructure management (i.e.; batch processing, system security features, backup and recovery etc.) in an isolated and controlled environment to validate that a quality system is ready for production.

因此端到端测试强调的是全面的，包含硬件环境等等的测试。

最后一句话很重要：是为了上production。

因为覆盖面广，因此一般都是人工测试。通常也没有专用工具来做端到端测试。

##功能测试 Functional Test##

Functional tests are related to integration tests, but refer more specifically to tests that test an entire system or application with all of the code running together, almost a super integration test.


##非功能测试 Non-funtional Test##

非功能测试在某公司，主要指除程序主要功能以外的附属功能。如GMI，log，report，failover等，为了监控程序运行，实现程序稳定性而附加的功能。


##acceptance tests 不知道中文是什么##

总的来说，acceptance tests 和 Functional Test是非常接近的，甚至有些地方认为二者完全一样。二者的异同在于：

functional testing: This is a verification activity; did we build the thing right? Does the software meet the business requirements?

For this type of testing we have test cases that cover all the possible scenarios we can think of, even if that scenario is unlikely to exist "in the real world". When doing this type of testing, we aim for maximum code coverage. We use any test environment we can grab at the time, it doesn't have to be "production" caliber, so long as it's usable.

acceptance testing: This is a validation activity; did we build the right thing? Is this what the customer really needs?

This is usually done in cooperation with the customer, or by an internal customer proxy (product owner). For this type of testing we use test cases that cover the typical scenarios under which we expect the software to be used. This test must be conducted in a "production-like" environment, on hardware that is the same as, or close to, what a customer will use. This is when we test our "ilities":

Reliability, Availability: Validated via a stress test.

Scalabilitiy: Validated via a load test.

Usability: Validated via an inspection and demonstration to the customer. Is the UI configured to their liking? Did we put the customer branding in all the right places? Do we have all the fields/screens they asked for?

Security (aka, Securability, just to fit in): Validated via demonstration. Sometimes a customer will hire an outside firm to do a security audit and/or intrusion testing.

Maintainability: Validated via demonstration of how we will deliver software updates/patches.

Configurability: Validated via demonstration of how the customer can modify the system to suit their needs.

简单的说，functional testing倾向测试软件的所有具备的功能。倾向于是否完全了所有的需求。

acceptance testing倾向测试的是尽量真实的用户体验。测试是否完成用户的实际需求，在完全和production相同或尽量类似的环境中。

同时，二者都应该是完全的黑盒测试。

下面这句话很重要：

**Acceptance Tests/Criteria (in Agile Software Development) are usually created by business customers and expressed in abusiness domain language. These are high-level tests to test the completeness of a user story or stories 'played' during any sprint/iteration.**

a business domain language指非开发人员可以理解的类自然语言。现在比较流行的框架是JBehave。


Acceptance test cards are ideally created during sprint planning or iteration planning meeting, before development begins so that the developers have a clear idea of what to develop. Sometimes (due to bad planning!) acceptance tests may span multiple stories (that are not implemented in the same sprint) and there are different ways to test them out during actual sprints. One popular technique is to mock external interfaces or data to mimic other stories which might not be played out during an iteration (as those stories may have been relatively lower business priority). A user story is not considered complete until the acceptance tests have passed.

也就是说在一个sprint中，如何确定开发人员是否完成了一个功能？标准就是对应的acceptance test通过。

这也就是Acceptance-Test Driven Development的来由。


##再总结一下白盒和黑盒测试：##

- White box testing means that you know the input, you know the inner workings of the mechanism and can inspect it and you know the output.
- With black box testing you only know what the input is and what the output should be.

因此通常情况下，UT是白盒测试，但是有时候也可以是黑盒。例如现在流行的测试驱动开发，UT是根据需求先于代码被创建出来的，此时的UT只知道我们有什么，然后希望看到什么，所以就是黑盒。

而其他的测试则大部分是黑盒测试。但是集成测试和回归测试也可以是白盒。

前面提到的，测试对源代码覆盖率的问题，理论上只有对白盒测试，这个指标才有意义。对与黑盒测试，代码覆盖率根本就不make sense。

对于某些领导提的，“我们这个集成测试要100%覆盖源代码”，基本就是脑子被门挤了。

但是需要说明的是，黑盒测试一样可以计算代码覆盖率，虽然我认为没有什么意义。

使用cobertura注入后，就可以方便的得到任何一个集成测试对源代码的覆盖率。具体可以参考我写的cobertura的介绍。


最后提一下目前流行的开源mock框架(因为我是developer所以尤其关注UT相关的工具)

较早的时候EasyMock是最流行的工具之一。

现在来看，EasyMock由于出现的较早，因此功能也比较少。使用EasyMock会遇到很多不容易mock的情况。

###Mocktio###
EasyMock之后流行的mock工具。特点是句法结构清晰，易理解。文档比较全，由于比较流行所以遇到问题容易找到解答。

Mockito足以解决大部分UT的mock需求。总得来说是非常不错的mock工具。

###PowerMock###
其实这个工具是在EasyMock和Mockito上扩展出来的，目的是为了解决EasyMock和Mockito不能解决的问题。

我在介绍PowerMock的文章中详细说明了这个工具可用于哪些特殊mock需求。

缺点是该工具文档较少，例子不全，使用时遇到问题不容易解决。同时PowerMock需要和EasyMock或Mockito配合一起使用。

因此必须先掌握EasyMock或Mockito。

###Jmokit###
[http://code.google.com/p/jmockit/](http://code.google.com/p/jmockit/)  
另外一个类似PowerMock的工具。这个工具我不准备介绍了(最近看mock工具看的审美疲劳了)。

该工具实现和PowerMock相同的功能因此如果不喜欢PowerMock可以选择这个工具。

相对PowerMock， 这个工具文档比较全，适于学习。


另外还有Jmock等等mock工具，非常之多也很杂。此外也有一些专用Mock工具，比如MockFTPServer。
---
title: iOS静态库SDK制作（包含第三方静态库）
date: 2016-11-18
categories:
- 技术笔记
tags:
- 静态库
- 动态库
- framework
- SDK
permalink: Static Library 

---

##		前言  
>	以下所涉及的框架和库只针对iOS而言，不确保在其他平台也适用。

最近由于公司业务需要，要求封装一个支付SDK，需要用到微信支付和支付宝，之前做过的Framework没有依赖其他第三方的库所以比较好做，这次有所不同；一开始我想把支付宝和微信支付的SDK全部融合进来，折腾一天才发现我之前的想法有很多误区，这样是根本行不通的，不过最后还是封装成功了，下面把我的经验分享出来，供有需要的同学少走弯路。 制作之前最好把功课做足，看看静态库和动态库到底是什么东西。  

<!-- more -->
转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)  

##		一.	静态库和动态库的详细介绍  
我们平时的工程中或多或少都要引入第三方的SDK，就算你没有引入第三方的，至少引用过系统的Framework吧？其实这些SDK和Framework都属于库，库又分为静态库和动态库，我们平时导入的第三方SDK有的是Framework，有的是.a，到底哪些是动态库，哪些是静态库呢？下面分别介绍静态库、动态库，Framework和.a以及.dylib/.tbd区别  	
###	一.	静态库与动态库
首先要解释一下什么是库，库(Library)其实就是一段编译好的二进制代码，加上头文件就可以供别人使用，一般会有两种情况要用到库：  

- 某些代码需要给别人使用，但是我们不希望别人看到源码，就需要以库的形式进行封装，只暴露出头文件。  
- 对于某些不会进行大的改动的代码，比方说很多大公司常用且很少变动的模块都会编译成库，这样做的好处一是可以节省编译时间，二来对于代码的管理也非常方便。  

因为库是已经编译好的二进制文件了，编译的时候只需要link一下，**既然提到了link那就有不同的形式了，静态和动态，与之相对应的就是静态库和动态库**。   

####	1. 静态库
平时我们用的第三方SDK基本上都是静态库，静态库的几个特点：  

-	在App项目编译的时候会被拷贝一份编译到目标程序中，相当于将静态库嵌入了，所以得到的App二进制文件会变大。
- 在使用的时候，需要手动导入静态库所依赖的其他类库。*（比如说某个SDK中使用到了CoreMotion.framework，在使用的时候需要手动导入。有的SDK需要link十几个系统库，这个时候非常恶心，只能一个一个手动加，这是静态库一个很大的不便之处。）* 
- 导入静态库的应用可以减少对外界的依赖，如果导入的是第三方动态库，动态库找不到的话应用就会崩掉，例如Linux上经常出现的lib not found。
- 静态库很大的一个优点是减少耦合性，因为静态库中是不可以包含其他静态库的，使用的时候要另外导入它的依赖库，最大限度的保证了每一个静态库都是独立的，不会重复引用。

####	2.	动态库  
这个是我们最常用的一类库，使用频率最高的UIKit.framework和Fundation.framework都属于动态库，所有.dylib和.tbd结尾的都属于动态库。动态库的几个特点：  

-	平时使用的系统库都放在iOS系统中，在你打包应用程序的时候这些库不会拷贝到你的程序中，当需要使用的时候会动态从iOS系统中加载它们，因为这个原因，动态库也被称作共享库。编译时才载入的特性，也可以让我们随时对库进行替换，而不需要重新编译代码。
- 	这些库是所有应用公用的，换一种说法就是节省了应用安装包的体积，这是区别静态库很重要的一个特点，因为静态库使用一次就要拷贝一次，非常浪费资源。  
-  动态库在制作的时候可以直接包含静态库，也能自动link所需要的依赖库。
-  使用动态库的时候不需要再次link依赖库，即导即用，这个就厉害了。**唯一需要注意的是在导入自己制作的动态库时，需要在Embedded Binaries中导入，不然会报错：image not found。此时这个动态库会跟静态库一样被拷贝到目标程序中进行编译，苹果又把这种Framework叫做[Embedded Framework](https://developer.apple.com/library/content/documentation/General/Conceptual/ExtensibilityPG/ExtensionScenarios.html)**  

**关于动态库要搞清楚一点，我们自己制作的动态库与系统动态库的区别，我们自己制作的动态库引入App项目的时候需要embed进项目，也就是要拷贝到目标程序中，这就有点不像动态库的特性了，苹果这么做也是考虑安全问题吧！**  
至于能不能正常上架，我也不清楚，查了大量资料都是抄来抄去没说清楚，我猜测是不能上架的，因为一般的第三方SDK也都是静态库的形式，我猜测一个重要原因是iOS的应用本来就是运行在沙盒里面的，不同应用之间不能共享代码，同时动态下载代码苹果肯定也是明令禁止的，所以动态库也就失去意义了。当然可能还有其他因素，欢迎交流学习！

###	二.	Framework、.a、.dylib/.tbd
####	1.	Framework  
Framework的英文释意是框架，主要由Headers、binary文件、.bundle这三部分构成，除此之外还有Info.plist和Modules，后两者主要记录Framework的版本之类的信息，一般都会删掉，不做讨论  

-	**Headers**  
包含我们在制作Framework的时候暴露的头文件，所有被暴露的.h都放在这里。
-	**binary文件**  
整个Framework的核心，所有代码都被编译成了这样一坨二进制文件，这里要注意的是添加的依赖库不会被编译进来，用的时候还需要重新link其他依赖库。  
-	**.bundle**   
资源文件都打包放在这里。在制作Framework的时候不可以把图片直接放在项目中，否则制作好之后图片是一张一张的出现在项目中非常乱，需要新建一个bundle将图片放进去，这里的bundle提供整个SDK的图片资源。  
**注意：**图片放进bundle之后不可以用`[UIImage ImageWithName:]`读取图片。要先找到bundle包再拿图片。  

这里要纠正一个误区
>	很多人认为系统的Framework就是动态库，我们自己制作的Framework就是静态库。  

其实Framework既可以是静态库也可以是动态库，这取决于编译成的Mach-O（就是那个二进制文件）是动态库还是静态库，Framework本质上并不是一个库，它是苹果为了方便开发者提供了一种库的打包方式，Framework会将Mach-O文件、头文件和资源包全都包含进来，不需要你再手动整理，我们也可以通过Xcode来制作framework动态库使用。
**所以总结： Framework是库的打包形式，既可以是动态库也是静态库。**

####	2.	.a静态库
这类静态库与Framework基本类似，不同的是在打包成.a文件的同时，还需要提供头文件，使用时相较于Framework比较麻烦，（例如[微信支付SDK](https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419319164&token=&lang=zh_CN)使用的是.a，不同的是[支付宝SDK](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.Ijm3sG&treeId=193&articleId=104509&docType=1)是以framework的形式打包的）。.a这样打包不够方便，而Framework编译完成暴露的头文件都已经放好了。 

####	3.	.dylib/.tbd 动态库 
这类动态库我们也经常用，基本上都是系统提供的，一般不能自己制作，就算你通过其他方式制作使用，也肯定不能上架的，这里没什么好讲的。 

##		二.	Framework的制作
动态库与静态库的制作流程基本一样，包括头文件的暴露等，唯一不同的是Mach-O文件的编译形式。本节将介绍Xcode制作Framework的过程，本次制作的Framework静态库依赖其他第三方静态库（Framework和.a）。

1>	新建工程
![新建Framework工程](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E6%96%B0%E5%BB%BA%E5%B7%A5%E7%A8%8B.png)  
这里要选Framework，如果选择右边的Static Library制作出来的是.a静态库。

2>	导入所有要打包的文件和其他第三方静态库  
正常导入要打包的文件就可以了，在导入第三方静态库的时候要注意，不要选择添加到target中，如果添加进去要去target里面把第三方静态库删掉（只需导入，不要添加进target）
![导入第三方静态库](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E5%AF%BC%E5%85%A5%E7%AC%AC%E4%B8%89%E6%96%B9%E9%9D%99%E6%80%81%E5%BA%93.png)  
导入第三方静态库之后再link依赖的系统库，像这样  
![link依赖库](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E5%AF%BC%E5%85%A5%E4%BE%9D%E8%B5%96%E5%BA%93.png)  
注意上面的运行目标，因为我用的是Xcode8，最低支持到iOS8。  
要打包的文件和第三方静态库全部导入完成    
![所有文件导入情况](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E9%A1%B9%E7%9B%AE%E6%96%87%E4%BB%B6%E5%AF%BC%E5%85%A5%E6%83%85%E5%86%B5.png)   

3>	项目性质修改  
把项目的membership需改为public，否则头文件暴露将会不正常  
![修改项目的membership](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E5%B7%A5%E7%A8%8B%E6%80%A7%E8%B4%A8.png)  

4>	暴露头文件  
将头文件暴露出去，供外界使用，所有的编译文件都在Project中，需要右击添加到public里面  
![暴露头文件](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E6%9A%B4%E9%9C%B2%E5%A4%B4%E6%96%87%E4%BB%B6.png)  

**5>	选择Mach-O的编译方式**  
这是最重要的一步，这一步决定我们制作出来的是静态库还是动态库，默认选择的是Dynamic Library，要手动选择Static Library
![Mach-O 形式](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E9%80%89%E6%8B%A9%E7%BC%96%E8%AF%91%E6%96%B9%E5%BC%8F.png)

6>	编译  
如果你的依赖库里面有lib开头的dylib动态库，此时应该会报错  
![动态库链接报错](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E7%B3%BB%E7%BB%9F%E5%8A%A8%E6%80%81%E5%BA%93%E6%8A%A5%E9%94%99.png)  
什么意思呢？大概就是没找到对应的库文件，因为tbd是苹果提供的新的动态库格式，之前都是dylib，不知道这里又抽什么风，下面解决问题。  

7>	tbd动态库报错修改  
先把原来的.tbd删掉，然后再次添加，这个时候选择add other，在弹出的窗口中按快捷键shift + command + G 调出finder的前往窗口，输入/usr/lib，然后添加相应的dylib动态库 
![修改的动态库](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E6%9B%BF%E6%8D%A2%E4%BE%9D%E8%B5%96%E5%BA%93.png)  
替换完成之后重新编译项目，生成Framework(可在Product文件中右击在finder中显示找到)  

8>	使用  
新建一个文件夹，将制作好的静态库拷贝出来放进去，再将第三方静态库拷贝到相同的文件夹中，此时只要将这个文件夹提供给外界使用就可以了，这是我写的测试demo验证打包好的SDK是否可以正常使用 
![制作完成使用](http://oeat6c2zg.bkt.clouddn.com/%E9%9D%99%E6%80%81%E5%BA%93%E5%8A%A8%E6%80%81%E5%BA%93%E5%88%B6%E4%BD%9C-%E5%88%B6%E4%BD%9C%E5%AE%8C%E6%88%90%E4%BD%BF%E7%94%A8.png)  
至此我们已经完成了Framework中包含其他第三方静态库的制作。  
**如果需要制作动态库，只需要在第5步中将Mach-O的形式改为Dynamic Library就可以了，其他步骤一样**   
 
如果有问题请在留言区留言，或者邮件给我，互相交流学习！  

---
title: Weex从入门到超神（一）
date: 2017-05-26 14:23:11
categories:  
- 技术笔记  
tags:  
- Weex  
- Vue  
- JS
- 前端  
permalink: weex-1  

---

![](http://oeat6c2zg.bkt.clouddn.com/Weex_logo.png)

随着移动端发展进入白热化阶段，很多中小型公司越来越注重于APP的更新迭代速度。加上去年微信小程序的问世，前端同学似乎迎来了“第二春”，越来越多的 Native 开发者感受到了前所未有的压力，人家已经打到家门口了，难道就这样两眼旁观吗？  
  
两年前 Facebook 团队发布了一个全新的移动端和前端无缝衔接的框架 React Native，很明显是用 React 开发的，支持在 Native 上运行的这么一个玩意，这相对于苹果漫长的审核机制的确是一个福音。可是 React 的学习曲线比较陡，网上大部分教程的性质都是 **“React Native 从入门到放弃”**，RN虽好，但是对于大多数移动开发者来说学习成本过高。   
<!-- more -->

去年阿里巴巴开源了一个类似 RN 的框架 **[Weex](http://weex.apache.org/cn/)** ，虽然面世才一年多，已经收获了广泛的关注，今年 Weex 已经被纳入 Apache 基金会的孵化项目。
![](http://oeat6c2zg.bkt.clouddn.com/Weex_Apache.png)

##		为什么选择 Weex  

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)  


作为 Native 开发者，我们很清楚 Native 走到今天所面临的困境，相较于前端比较呆板不够灵活，任何改动都需要重新打包提交审核然后发布版本，这个周期最短也要1~2天的时间，一直有人在说要用 H5 替代 Native ,这不是危言耸听，移动端市场正在遭受着冲击。  

大部分中小型的互联网公司都是小步快走的模式进行版本迭代，版本发布的灵活性就显得尤为重要，可能产品早上想的功能点晚上就要上线，Native 肯定是办不到的，H5 这个时候就显示出它的优势了；但是 H5 有一个致命的缺点就是性能太差，用户体验远达不到 Native 带来的那种丝滑流畅般的享受。所以这两年，RN 和 Weex 悄然崛起就是为了解决这种矛盾。

不管是 RN 还是 Weex 都能做到实时修改页面不需要 Native 发版，他们的原理都是一样的，通过 js 来渲染 Native 界面。  
Weex 在很大程度上借鉴了 RN 的思想和方式，对比一下 RN 和 Weex 的差异和优缺点：  

###	优点
-  由于 Weex 采用了 Vue 作为上层框架，相较于 React 更加轻量，Vue 的官网宣传就是非常轻量，体积小巧，语法简单。
-  Vue 的学习成本相较于 React 更加小，大部分 Native 开发者更容易上手。
-  Weex 吸收了 RN 的精华，可以说 Weex 是站在巨人的肩膀上问世。


###	缺点

-	Weex 相较于 RN 起步比较晚，社区没有 RN 活跃。
- 	从问世的时间上来看，RN 具有更大的优势，Weex 的学习资料比较少。
- 	Weex 现在存在的 BUG 相较于 RN 还比较多，对于使用来说会有一些影响。

不管选择 RN 还是 Weex ，我们的目的都是一样：通过 js 语法渲染成  Native 的页面，至于该选择哪个，这就要结合自己公司的实际情况来选，没有绝对的好与坏。  
由于我们公司的 H5 项目是用 Vue 开发的，所以我们也就毫不犹豫的选择了 Weex。  

![](http://oeat6c2zg.bkt.clouddn.com/weex&vue.png)  

可能大部分 Native 开发者看到这里就要说一句：*球都麻袋！Weex 都还搞明白怎么又提到 Vue ，这是什么鬼*；Vue 是国人开发的一个 JS 框架，大家可以去官网看看，文档都是中文比较方便，这里就不再赘述，有一点 H5 基础都可以很快上手。**[Vue官网](https://cn.vuejs.org)**

##		Weex 项目结构  
想必大多数 Native 开发者对于前端的知识还是匮乏的，虽然 Weex 官网有教程会教你怎么安装怎么运行，大部分同学任然会卡在某一个步骤走不下去，所以基础工作还是要做好，后面的路才会顺畅。  
  
首先给大家介绍 Node.js 和 npm ，刚开始接触这个我也是懵逼的，这两者之间有什么关系？为什么要安装 Node.js ？ 搞懂这个关系后面对 weex 中结构理解会有很好的帮助，npm 是 Node.js 默认的包管理器，从 Node.js 0.6.3 开始，npm 集成到了 Node.js 的安装包里面，所以我们安装 Node.js 的目的是使用 npm 来管理 weex 所用到的一些依赖库。

至于怎么安装，可以参考 Weex 的[官方教程](http://weex.apache.org/cn/guide/)

>  前端同学用到的 npm 有点类似我们用的 Cocopods 来管理第三方依赖库，安装 Cocopods 之前你必须安装 ruby ，因为 Cocopods 依赖 ruby 才能运行， npm 也是一样的道理，npm 依赖 Node.js 才能运行。

Weex 的文件格式有两种，分别是 `.we` 、`.vue`，可以很明显的发现用 Vue 可以直接写 Weex 页面。笔者开始接触 Weex 的时候也是直接学 Vue ,不仅可以用来写 Weex 还可以写写其他 H5 页面。 **所以我建议学 Weex 直接看 Vue 就可以了。**

###	Weex 的目录结构

 ```JavaScript

├── src  
├── node_modules 
├── dist
├── build
├── bin
├── package.json
├── webpack.config.js    
└── config.js   
        
 ```

**src**  
> 源码存放的位置，如`.we` `.vue`  

**node_modules** 
> 依赖库的存放位置，类似于Xcode项目中的 Pods 文件夹。在 package.json 所在目录执行 npm install 就会自动安装好所有的依赖，有点像 pod install。
  
**dist**  
> 存放编译好的js文件 
 
**build**
> 存放npm build 时的 js 文件，可在 package.json 文件中配置

**bin**  
> 存放一些 shell 脚本，一般用不到

**package.json**  
> 项目的配置和依赖库文件，有点类似 podfile 文件

**webpack.config.js**
> webpack 的配置文件

**config.js**  
> 项目的相关配置文件，你可以在这个文件中配置切换不同的环境

提到 webpack ，这个比较复杂，我们只需要知道 Weex 用 webpack 进行打包编译就行了，当然也可以用其他工具来打包；感兴趣的同学可以看一下 webpack 的[官网](http://webpack.github.io)。  
当你运行 `npm bulid` 时，对应的是运行 package.json 中配置的 `scripts: build` 命令，src 文件夹中的文件都会被编译好并存放到 dist 文件夹中，这个路径在 webpack.config.js 文件中可以进行配置。`npm run` 后面跟的命令都是在 package.json 的 `scripts` 配置的。  

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)   

Weex 前端的项目目录大概就是这样，Weex 前端的源码不在这次的讨论范围之类，如果大家感兴趣想看 Weex 前端的源码，在 node_modules 文件夹中就可以找到。**关于 Weex SDK源码在后续文章中会进行深度解析。**
##		Weex 运行原理 
官方也给出了 Weex 的运行原理图，顺手牵羊拿了过来：

![](http://oeat6c2zg.bkt.clouddn.com/Weex_theroy.png)  

不难发现，Weex 其实就是将 `.vue` 、`.we` 文件编译成 js 文件，打包成所谓的 JS Bundle 放到 dist 文件夹中，然后将编译好的 JS Bundle 部署到服务器上，我们的 iOS、安卓、浏览器就可以访问对应的 JS 然后由 SDK 渲染成 Native 的页面，或者浏览器的内核渲染成 DOM 节点显示。**这里有个坑要提一下：虽然说是三端统一的，实际开发中还是要做兼容处理的。**  

> 本篇文章浅显的介绍了 Weex 的应用背景和工作原理，下篇文章将深入分析 Weex 的实现原理。 

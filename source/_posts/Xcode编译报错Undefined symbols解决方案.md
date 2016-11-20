title: Xcode编译报错Undefined symbols解决方案
date: 2016-03-16
categories:
- 跳坑指南
tags:
- Xcode
- Cocopods
permalink: Xcode编译报错Undefined symbols解决方案

---
####  当我们用cocopods管理第三方类库时，经常遇到编译报错的问题：

```
`Undefined symbols for architecture x86_64:
  "_OBJC_CLASS_$_AFHTTPRequestOperation", referenced from:
      objc-class-ref in ZRAPIClient.o
  "_OBJC_CLASS_$_AFHTTPRequestSerializer", referenced from:
      objc-class-ref in ZRAPIClient.o
  "_OBJC_CLASS_$_AFJSONResponseSerializer", referenced from:
      objc-class-ref in ZRAPIClient.o
  "_OBJC_CLASS_$_BITHockeyManager", referenced from:
      objc-class-ref in ZRAppDelegate.o`
```

<!-- more -->

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)
网上各种说法都有，不过每个人遇到的情况可能不一样，个人总结了3个方案供参考：
#####  所连接的静态库不支持 x86_64，解决方案：

1. 打开Pods的`Build Setting` ，添加`X86_64`architecture
2. 设置`Build Active Architectures Only`为`NO`
3. Clean Pods
4. Build 项目  


#####  OtherLink Flags问题，解决方案：

打开项目的`TARGETS` > `Build Settings` >`OTHER_LDFLAGS `
添加` $(inherited)`

##### 编译文件出错，解决方案：
1. 找到
`/Users/***YourName***/Library/Developer/Xcode/DerivedData/***YourProject***/Build/Products/Debug-iphoneos`
2. 这里可以使用terminal命令行打开，打开终端输入 `open "上面的路径"`可以直接打开目录
3. 删除当前报错项目的编译文件，回到项目里面重新Build就不会报错了

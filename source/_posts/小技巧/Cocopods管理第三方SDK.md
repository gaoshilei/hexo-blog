---
title: 如何使用Cocopods管理第三方SDK
date: 2018-1-19
categories:
- 小技巧
tags:
- Cocopods
- SDK
permalink: cocopods_private_sdk_repo  
---

最近整理项目，发现用到了很多第三方的SDK，这些SDK都是直接拖到项目里面的，这么做有两点不好：  

- SDK的lib包至少都是5M+，看着不是很大，但是当添加到git中将会是一个庞大的储存空间开销（不添加到git中不方便团队开发管理）
- 当升级SDK的时候比较麻烦（次要原因）

主要基于第一种原因，打算把这些乱七八糟的第三方SDK全都交给 Cocopods 来管理，这样 SDK 不会添加到 git 中，不会导致项目 git 仓库提交了两个月之后变成 1G+ 这种悲剧发生。

<!-- more -->

# 什么是Cocopods？

 ![一脸懵逼](http://oeat6c2zg.bkt.clouddn.com/DBCC6999A0786EF4772B24C1C0A97722.jpg)  
 你不知道 Cocopods 是什么？给你个传送门 [https://cocoapods.org](https://cocoapods.org)

# Cocopods 新建本地仓库

这里我用微信 SDK 来举个栗子，从微信开发者中心下载对应的 SDK。

 <img src="http://oeat6c2zg.bkt.clouddn.com/timg.jpeg" width = "50%" height = "50%" alt="举个栗子" align=center />  

 我们得到一个 WechatSDK 文件夹，里面的内容也比较简单

 ```JS
└── WechatSDK  
    ├── libWeChatSDK.a 
    ├── README.txt
    ├── WechatAuthSDK.h
    ├── WXApi.h
    └── WXApiObject.h  
```

要让 Cocopods 来管理第三方 SDK，我们需要将第三方 SDK 制作成一个仓库，跟平时我们使用 Podfile 一样。 下面我们要在  WechatSDK 目录下新建一个 `.podspec` 格式的文件，这个文件主要是用来描述当前仓库的一些信息，它的格式官网有介绍，不赘述。[http://guides.cocoapods.org/syntax/podspec.html](http://guides.cocoapods.org/syntax/podspec.html)  

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)   

按照他要求的格式，新建 WechatSDK.podspec 并填入下面这些信息：

```ruby
# coding: utf-8
Pod::Spec.new do |s|
  s.name         = "WechatSDK" #必填，仓库的名称，Podfile中会用到，类似于 AFNetworking

  s.version      = "1.8.2" #必填，版本号

  s.summary      = "微信SDK" # 随便写写吧

  s.description  = <<-DESC # 随便写写吧
                    WechatSDK repo
                     DESC

  s.homepage     = "http://git.internal.weyao.com/gaoshilei/WechatSDK" # 随便写写吧
  s.license    =  'MIT' # 随便写写吧
  s.authors      = { "gaoshilei" => "goslei@163.com" } # 随便写写吧
  s.platform     = :ios # 必填
  s.ios.deployment_target = '8.0' # 必填
  s.source =  { :git => './Vendors/WechatSDK', :tag => "1.8.2" } # 必填，这是你的仓库相对于 Podfile 的路径（我试过写绝对路径，最后报错了）
  s.source_files = '*.{h,m,mm,c}' # 必填，代码文件。如果你还有二级目录，要包含所有二级目录中的代码文件，用**表示。上面给的链接中也有介绍
  # s.frameworks = 'QuartzCore', 'CoreData' #这里是第三方 SDK 使用到的一些系统 Framework
  s.vendored_libraries = 'libWeChatSDK.a' # 如果第三方 SDK 有lib包，这个是必填的（注意路径）
  # s.vendored_frameworks = 'ThirdPartyFramework.framework' #第三方SDK如果有 Framework，需要在这里加上（注意路径）
  s.requires_arc = true # 加上就行，除非你还在写MRC的代码

end

```

 `s.source` 这个键需要详细讲解一下。这是 Cocopods 需要读取的 git 仓库地址，这里直接写成本地的仓库路径就可以了，不过要在 WechatSDK 文件夹中新建 git 仓库。然后 tag 能对应上就可以了。在当前目录下执行下面的命令：

 ```
git init 
git add.
git commit -m "commit"
git tag 1.8.2
 ```

注意 git 仓库地址的路径要填相对于你项目 Podfile 的路径，我的项目 Podfile 跟 文件夹 Vendors 是同级的，所以我应该这么写 `./Vendors/WechatSDK` 。  
到这里工作已经完成一大半了，下面就是要在项目 Podfile 文件中正确配置  

```ruby
  pod 'AFNetworking'
  ......
  pod 'WechatSDK', :podspec => './Vendors/WechatSDK/WechatSDK.podspec'
  ......
```

后面指定仓库配置文件的路径就可以了，这里也要注意是相对于 Podfile 文件的路径。然后在项目中执行 `pod install --no-repo-update` 安装，一般可能会有以下的问题（我在制作过程中遇到的）  

第一种情况： 

```ruby
[!] Failed to load 'WechatSDK' podspec:
[!] Invalid `WechatSDK.podspec` file: undefined local variable or method `tag` for Pod:Module
```

这种情况是 Cocopods 没有找到仓库的 podspec 配置文件，原因是 Podfile 中的路径写错了，改成仓库相对于 Podfile 的路径就可以了。

第二种情况：  

```ruby
[!] Error installing WechatSDK
[!] /usr/bin/git clone $HOME/Desktop/LittleBee/LittleBee_iOS/Vendors/WechatSDK /var/folders/6y/w9bcrs915g17gt732n84x6p40000gn/T/d20180119-75062-1jdxrw8 --template= --single-branch --depth 1 --branch 1.8.2

fatal: repository '$HOME/Desktop/LittleBee/LittleBee_iOS/Vendors/WechatSDK' does not exist
```

这就很明显了，仓库找不到，因为 `WechatSDK.podspec` 中`s.source`路径写的是绝对路径，解决方法就是改成相对路径。  


第三种情况：

```ruby
[!] The `WechatSDK` pod failed to validate due to 1 error:
    - ERROR | [iOS] File Patterns: File patterns must be relative and cannot start with a slash (source_files).
```

这种情况就是 podspec 配置文件格式不对，对照官网的文档修改一下就行。   

**上面是将第三方 SDK 制作成了 Cocopods 库，你也可以将你自己的代码制作成库，将 s.source 改成 github 上的地址，就制作了一个线上可以共享的 cocopods 库，类似于 AFNetworking，这个要多一个步骤，将自己的开源库配置文件推送到 Cocopods 的 podspec 仓库中（我还没有制作过，具体步骤自行百度或者谷歌吧）**

# 创建私有仓库管理中心  

上面都完成，貌似是挺完美，但还是有缺陷的。明显跟我们平时使用的 pod 格式不一样，后面还要配置路径，好麻烦！  

```ruby
  pod 'AFNetworking'
  pod 'WechatSDK'
  ......
```

如果能这样用那岂不就完美了。Cocopods 其实是通过 podspec 来管理所有的仓库的，在我们的本地有一个目录 

```shell
~/.cocoapods/repos
```

Cocopods 把中心仓库放在了这个位置，所以平时我们执行 `pod install` 都会去这个中心仓库查看是否有对应的目标开源组件，然后`git clone`下来，所以有时候明明有这个开源组件，但是我们执行 `pod install` 总提示安装失败，没有这个目录。那是因为本地的 repos 太旧了，这个时候执行 `pod repo update` 一下就可以了。基于 Cocopods 这个原理，我们就可以实现上面提到的方式了。

先看下 Cocopods 的中心仓库是怎么管理这些开源插件的

![AFNetworking](http://oeat6c2zg.bkt.clouddn.com/QQ20180119-204806@2x.png)  

路径是这个样子的  

```shell
LeonLeiMBP15-145:AFNetworking gaoshilei$ pwd
/Users/gaoshilei/.cocoapods/repos/master/Specs/a/7/5/AFNetworking
LeonLeiMBP15-145:AFNetworking gaoshilei$ cd 3.1.0/
LeonLeiMBP15-145:3.1.0 gaoshilei$ ls -o
total 8
-rw-r--r--  1 gaoshilei  2889 12 19  2016 AFNetworking.podspec.json
```

AFNetworking 下面有很多版本号的文件夹，每个版本号下面对应的是仓库的配置文件.podspec格式化的json文件。照葫芦画瓢我们就可以创建自己的私有中心仓库。找个目录建立自己的私有中心仓库  

```shell
LeonLeiMBP15-145:~ gaoshilei$ cd Desktop/
LeonLeiMBP15-145:Desktop gaoshilei$ mkdir CocopodsPrivate
LeonLeiMBP15-145:Desktop gaoshilei$ cd CocopodsPrivate/
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ mkdir WechatSDK
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ cd WechatSDK/
LeonLeiMBP15-145:WechatSDK gaoshilei$ mkdir 1.8.2
LeonLeiMBP15-145:WechatSDK gaoshilei$ cd 1.8.2/
LeonLeiMBP15-145:1.8.2 gaoshilei$ cp ~/Desktop/LittleBee/LittleBee_iOS/Vendors/WechatSDK/WechatSDK.podspec .
```

此时私有中心仓库已经建好了，下面就是要让 Cocopods 知道这个仓库的存在，为了方便团队开发时直接使用，这个中心仓库需要放到公司 git 上共享：  

```shell
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ git init
Initialized empty Git repository in /Users/gaoshilei/Desktop/CocopodsPrivate/.git/
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ git add .
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ git commit -m "first commit"
[master (root-commit) aa27f56] first commit
 1 file changed, 25 insertions(+)
 create mode 100644 WechatSDK/1.8.2/WechatSDK.podspec
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ git remote add origin git@git.internal.weyao.com:gaoshilei/CocoapodsPrivate.git
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ git push origin master
```

然后再将这个私有中心仓库添加到 Cocopods 中  

```shell
LeonLeiMBP15-145:CocopodsPrivate gaoshilei$ pod repo add CocoapodsPrivate git@git.internal.weyao.com:gaoshilei/CocoapodsPrivate.git
```


添加成功之后，执行 `pod search WechatSDK` 可以看到，刚才添加的已经可以搜到了，并且版本号后面显示来自仓库`CocoapodsPrivate`  

![私有仓库搜索结果](http://oeat6c2zg.bkt.clouddn.com/QQ20180119-211208@2x.png)  

让团队其他成员执行 `pod repo add CocoapodsPrivate git@git.internal.weyao.com:gaoshilei/CocoapodsPrivate.git` 之后，就可以使用这个私有中心仓库了。  


PS：当你可以搜到 `WechatSDK` 时却无法正常执行 `pod install`，会报这样的错：`[!] Unable to find a specification for 'WechatSDK'` ，那是因为项目的 Podfile 中需要添加响应的仓库地址才行：

```shell
platform :ios, '8.0'
source 'https://github.com/CocoaPods/Specs.git'
source 'git@git.internal.weyao.com:gaoshilei/CocoapodsPrivate.git'
......
  pod 'WechatSDK'
......
```

把这两条添加进去，然后再执行 `pod install` 就没问题了。



---
title: VPS搭建高速SS服务器
date: 2016-05-20
categories:
- 实用工具
tags:
- VPS
- VPN
- Shadowsocks
permalink: VPS

---

##		前言：(废话较多，不想看的略过直接看后面的教程)  
*	作为一名有着远大理想和抱负的codeMonkey，平时查资料必须Google，百度一下会真的死啊！不是黑百度，确实百度出来的资料内容看一下大致是相同的，搜到的内容就是copy+paste，花了很多时间结果找不到我们想要的东西，最最重要的是搜索结果有一半是广告，这个时候只能求助于Google，无奈天朝的GFW，一直追求自由明主的Google早在10年就被GCD轰出了墙外，所以VPN成了连接我们和整个世界的桥梁。
<!-- more -->

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)

*	现在市面上的VPN产品满天飞，有不少是开张几个月就卷款跑路，然后重新弄个网站换个名字继续骗钱，市面上常见的VPN还有一个很大的缺点就是速度不稳定，只能够全局加速（至少在Mac上是这样），访问国内网站都很卡，因为这些VPN都是共享一条线路，用户少速度会快一点，人一多就卡成了龟速。当然也有部分VPN推出了专线套餐，便宜的一个月也要100大洋左右，我等屌丝“何德何能”能消费得起这样的产品啊（鬼魅的微笑）。  
*	在用了几年这种VPN产品之后，我终于发现了一块新大陆，自己购买主机搭建SS服务器，不论是速度还是用户体验，不要太爽的好伐，关键是价格很亲民，最便宜的一年20刀，折合人民币才100多大洋。接下来就给大家分享我搭建SS的过程，搭建完成之后观看YouTube高清720P毫无压力（当然还要取决于运营商给你的带宽）。我购买的是VPS界享有“盛誉”的搬瓦工，价格亲民、速度快，有智能后台一键搭建VPN省去很多繁琐的命令行输入，大家可以在官网首页看到机型配置和价格，最便宜的2.99刀一个月，一年20刀。

##	教程  
###	一.	购买VPS  
> VPS有点像VirtualBox、Parallels创建出来的主机，可以理解成一台独立的主机。我们需要购买的就是这样一台独立的主机，不过一定要购买海外的，否则搭建了SS也无法访问海外的网站。  
   
因为我用的是搬瓦工，速度和稳定性感觉都不错，推荐给大家，还有其他的海外VPS提供商也都是可以的。
**搬瓦工官网链接：[https://bandwagonhost.com](https://bandwagonhost.com/aff.php?aff=10505)**    
这个链接貌似被墙了，如果访问不了的话请走大陆**镜像链接：[https://bwh1.net](https://bwh1.net/aff.php?aff=10505)**   

进入之后要注册，之后就可以购买主机了，根据你自己的需求来选择。（*其实不同主机的带宽都是一样的，只不过在配置上有差别，如果不是搭建大型的网站对配置有要求，只是想有个专线VPN或翻墙工具的话，$19.99 或者 $39.99一年就足够用了。*）  

> **我在购买主机的时候有一个小坑要提一下，~~搬瓦工的支付方式只支持PayPal，国内强大的支付宝居然不能支付！所以又去注册一个PayPal，~~坑来了：** 
PayPal分国内版和国际版，国内版是不支持美元支付的，而且两者的账户是不通的，所以你注册了国内版是无法支付的，国际版的地址是：[https://www.paypal.com](https://www.paypal.com/c2/webapps/mpp/home)，虽然是中文，但是货币是USD美元，绑定一张银联的卡就可以购物了。
<img src="http://oeat6c2zg.bkt.clouddn.com/%E6%90%AD%E5%BB%BAVPNPayPal.png" width="500"/>   
 
**这里做个修正：搬瓦工已经推出支付宝支付了，check out的时候选择alipay就可以了**

###	二.	配置服务器  
####	1.	进入控制面板，修改当前的root密码  
进入账户之后我们可以在MyServices中看到服务器列表：
![服务器列表](http://www.leonlei.top/%E6%90%AD%E5%BB%BAVPN%E6%9C%8D%E5%8A%A1%E5%99%A8%E5%88%97%E8%A1%A8.png)  
进入KiwiVM管理后台，我们可以看到左侧有个菜单栏，点击Root Shell-interactive，此时会以H5的形式打开一个terminal窗口，执行`passwd`命令修改root密码  
（*如果你不嫌系统分配的root密码不好记、每次ssh进主机都要复制粘贴密码，那么略过这步，***如果你忘记了root密码也可以直接通过这里修改，什么？！你忘记搬瓦工的账号密码无法进入后台面板？用你注册填写的邮箱或者手机号找回吧！**）
![修改root密码](http://www.leonlei.top/%E6%90%AD%E5%BB%BAVPN%E4%BF%AE%E6%94%B9root%E5%AF%86%E7%A0%81.png)

####	2.	安装一个你喜欢的Linux OS  
左侧菜单栏找到Install New OS，选一个你喜欢的系统吧（*系统默认安装的是32位CentOS6，如果你不想换其他系统这步也可以略过，***需要注意每次安装系统，主机所有数据都会丢失**）  
<img src="http://oeat6c2zg.bkt.clouddn.com/%E6%90%AD%E5%BB%BAVPN%E5%AE%89%E8%A3%85%E6%96%B0%E7%B3%BB%E7%BB%9F.png" width="500"/>    
这里推荐安装64位系统，后面装插件支持都好一点。
####	3.	安装Shadowsocks Server  
> 搬瓦工也提供了openVPN一键安装，个人感觉Shadowsocks更好用，有两种加速模式，访问会更快速。  
  
**2017.11.16更新：** 
现在搬瓦工的后台也可以一键安装 ShadowsocksR Server（SSR）了，操作流程基本一致。

左侧菜单栏找到Shadowsocks Server，点进去安装就好了（**注意：搬瓦工提供的一键安装功能只支持CentOS6**，你也可以通过命令行的方式安装），安装好的Shadowsocks Server界面是这样的：  
<img src="http://oeat6c2zg.bkt.clouddn.com/%E6%90%AD%E5%BB%BAVPNShadowsocks%20Server.png" width="500"/>  
此时SS已经可以用了，不过还差一个客户端，Windows版本的客户端在后台面板就有链接，Mac用户请[点击这里下载](https://sourceforge.net/projects/shadowsocksgui/)如果无法访问，我已经下载好放到我的网盘了[ShadowsocksX-2.6.3.dmg](https://pan.baidu.com/s/1boXspQJ)，安装好打开Shadowsocks Server，在Mac的工具栏会有一个小飞机的图标  
<img src="http://oeat6c2zg.bkt.clouddn.com/%E6%90%AD%E5%BB%BAVPNShadowsocks%20Server%E4%BD%BF%E7%94%A8%E7%95%8C%E9%9D%A2.png" width="300" height="400" />  

**2017.11.16更新：**  
由于SS服务在部分地区受到运营商的流量干扰，出现网速慢甚至断网的现象，有类似情况的朋友请安装SSR，抗干扰效果更好。请参考我近期写的一篇文章[VPS+SSR+锐速（BBR魔改版）实现超级加速](https://gaoshilei.com/2017/11/06/SSR/)  
你购买或者配置VPS过程中遇到什么问题，可以通过邮箱 goslei1315@gmail.com 联系我，工作日一般2个小时之内回复。询问之前请描述清楚你遇到的问题。

>  2016.11.25更新：由于iPhone的Shadowsocks Server只在英国地区销售，国内的AppStore是下载不到的，大家可以在AppStore搜wingy，配置过程跟mac差不多，主要是IP、 Port和密码，加密协议都用默认的aes-256-cfb就行，然后手机也可以愉快的上网了。

点开服务器，配置IP和密码，只需要修改地址和密码，其他不用改就OK了。
<img src="http://oeat6c2zg.bkt.clouddn.com/%E6%90%AD%E5%BB%BAVPNShadowsocks%20Server%E8%AE%BE%E7%BD%AE.png" width="500" height="300"/>  
上两张图显示Shadowsocks Server有两种加速模式 ，**一般情况下勾选自动代理模式就可以了，这个这个模式下会自动判断你当前访问的域名是否在GFW名单里面，如果是就启用代理，如果不是就正常访问，这样我们在访问墙内网站的时候也不会受到任何影响** ，如果你遇到网站无法访问，有可能是这个网站近期被墙了，你没有更新本地的GFW名单，如果你确定这个网站是可以打开的，切换到全局模式就可以访问了 
> Shadowsocks Server自动代理模式原理是根据GFWList配置了一个PAC文件，名单中的域名全部走代理，你可以手动修改这个配置文件，添加你要访问的被墙的网站，它就是一个js文件，你点击编辑自动模式的PAC文件便会跳转到这个js所在的位置，那个GFWList自动更新功能坏掉了，作者一直也没更新，不过不影响平时使用。  
  
**2017.11.16更新：**
**请注意：下面的内容已经过时，更稳定更便捷更快速的翻墙姿势请查看我近期写的一篇文章。**  
传送门：[VPS+SSR+锐速（BBR魔改版）实现超级加速](https://gaoshilei.com/2017/11/06/SSR/)

###	三.	加速SS（很重要！很重要！很重要！）
完成上面的步骤，你确实是可以访问墙外网站了，但是下载速度一般只有100多KB，YouTube视频240P都感觉不流畅，此时就要用到Net-Speeder给VPN加速了，具体步骤请看：  
#####	1.	先连上远程主机
`ssh -l root -p 12830 192.243.112.242`  
把端口和IP换成你自己主机的，然后需要输入root密码，输入在第一步我们设置的密码就可以了。  
#####	2.	安装Net-Speeder  
输入下面的命令进行安装：  
`wget https://coding.net/u/njzhenghao/p/download/git/raw/master/net_speeder-installer.sh`
这里我用的是别人git上的sh脚本，有现成的为何不用呢，是吧？！
#####	3.	编译并安装  
输入下面的命令编译Net-Speeder：  
`bash net_speeder-installer.sh`   
命令执行成功之后，执行reboot重启主机，或者在后台面板重启主机也行。（**此时远程主机的连接会断开，需要重新连接**） 
#####	4.	端口加速  
最后一步，加速端口：  
`nohup /usr/local/net_speeder/net_speeder venet0 "ip" >/dev/null 2>&1 &`  
执行完这个命令应该会有一个端口号打印出来，证明加速成功了！别着急还有最后一步，点开Shadowsocks Server菜单点击退出，*不要点退出Shadowsocks Server*，然后再次打开App，现在打开YouTube看个视频试试吧！现在墙外网站下载速度一般都在500KB左右，当然这个速度也受到你所在运营商的网络环境影响。（**注意：加速端口这个命令每次重启主机都需要执行一次，因为这个脚本没有加到开机自启动，反正我们没事也不重启主机，我懒得弄了，大家自己Google吧，哈哈！**）  

**2016.11.25更新**  

有些网友反应速度有时候很慢，我今天也遇到了这种情况，解决方案如下：  
先通过命令连上VPS  

```
ssh -l root -p port IP
```

然后重启主机  

```
reboot
```

此时连接断开，不用管，去看一下此时的SS是否正常使用，确定可以访问之后，再连上VPS开启端口加速  

```
nohup /usr/local/net_speeder/net_speeder venet0 "ip" >/dev/null 2>&1 &
```  

这种情况应该是主机的SS服务挂掉了，这种情况很少遇到，我使用了这么久今天第一次遇到，这么操作之后SS又恢复到原来丝滑般的享受 。

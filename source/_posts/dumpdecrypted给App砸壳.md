title: dumpdecrypted给App砸壳
date: 2016-08-09
---
#### 1.前言
> 我们都知道从AppStore下载的应用二进制文件被苹果进行了加密处理，也就是我们俗称的*壳*，我们要想对目标App进行逆向分析，必须解密目标二进制文件，俗称*砸壳*。  
> long long ago有一种傻瓜式的砸壳方式，利用iPhoneCake源的AppCrackr进行一键砸壳，这种方式简单粗暴，省时省力，但正是因为它过于方便，导致几乎所有用户都可轻松上手，随便亵玩，所以不少用户都拿它来破解程序，这也导致了iOS越狱开发社区普遍认为这个软件助长了盗版的气焰，对iPhoneCake源进行了强烈谴责。迫于压力，iPhoneCake将AppCrackr下架。从此利用纯UI方式砸壳的行为已经走入绝路，只能利用更加geek更加niubility的方式来砸壳，这也是这篇文章介绍的主角**dumpdecrypted**  

<!-- more --> 
#### 2.准备工作
1. 一部已经越狱的手机 `我这里用的是iPhone 5S; iOS 9.1`
2. 已经安装了OpenSSH
3. 已经安装了[Cycript](http://www.cycript.org)
4. [dumpdecrypted源码](https://github.com/stefanesser/dumpdecrypted/archive/master.zip)  

#### 3.编译dumpdecrypted
下载好之后将文件放到你自己的文件夹中，下面开始编译：  
 
```  
LeonLei-MBP:~ gaoshilei$ cd /Users/gaoshilei/Desktop/reverse/dumpdecrypted  
LeonLei-MBP:dumpdecrypted gaoshilei$ make
`xcrun --sdk iphoneos --find gcc` -Os  -Wimplicit -isysroot `xcrun --sdk iphoneos --show-sdk-path` -F`xcrun --sdk iphoneos --show-sdk-path`/System/Library/Frameworks -F`xcrun --sdk iphoneos --show-sdk-path`/System/Library/PrivateFrameworks -arch armv7 -arch armv7s -arch arm64 -dynamiclib -o dumpdecrypted.dylib dumpdecrypted.o
```
进入dumpdecrypted目录下之后，执行make命令，此时目录下会生成一个`dumpdecrypted.dylib`，这个文件生成一次即可，下次砸壳可以直接使用。

#### 4.开始砸壳  
##### 定位目标App可执行文件的位置  

```  
LeonLei-MBP:~ gaoshilei$ ssh root@192.168.0.115
iPhone-5S:~ root# ps -e
  PID TTY           TIME CMD
    1 ??         5:23.51 /sbin/launchd
   23 ??         0:00.81 /usr/libexec/amfid
   34 ??         1:28.92 /usr/sbin/mediaserverd
   36 ??         4:23.49 /usr/libexec/fseventsd
   38 ??         1:21.05 /System/Library/PrivateFrameworks/AssistantServices.framework/assistantd
   40 ??         0:01.13 /System/Library/PrivateFrameworks/FileProvider.framework/Support/fileproviderd
   42 ??         1:56.46 /usr/libexec/routined
   46 ??         0:03.34 /System/Library/PrivateFrameworks/MediaRemote.framework/Support/mediaremoted
   48 ??         0:00.86 /usr/libexec/misd
   50 ??         0:18.48 /System/Library/Frameworks/HealthKit.framework/healthd
   52 ??        19:18.39 /usr/libexec/configd
   54 ??         3:30.26 /System/Library/CoreServices/powerd.bundle/powerd
   58 ??         0:50.73 /usr/libexec/atc
   60 ??        13:47.50 /usr/sbin/wifid
   ···              ···
 5673 ??         0:04.41 /var/mobile/Containers/Bundle/Application/2A4313C7-6B36-40AF-9BEC-2C77FF1AC484/WeChat.app/WeChat
 5732 ??         0:00.32 /usr/libexec/ptpd -t usb
 5735 ??         0:00.07 /usr/libexec/webinspectord
 5741 ??         0:00.18 sshd: root@ttys000 
 5770 ??         0:00.16 /System/Library/PrivateFrameworks/SyncedDefaults.framework/Support/syncdefaultsd
 5785 ??         0:00.05 /System/Library/CoreServices/CFNetworkAgent
```
可以看到目前手机运行的进程中有微信的影子`/var/mobile/Containers/Bundle/Application/2A4313C7-6B36-40AF-9BEC-2C77FF1AC484/WeChat.app/WeChat` 我们已经找到微信可执行文件的位置
##### 目标锁定，定位到目标App的Documents位置  
 
```  
iPhone-5S:~ root# cycript -p WeChat  
cy# [[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask][0]
#file:///var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents/  
```

执行到这里我们已经找到了微信的Documents位置，正式开始砸壳！
> 这里有两种方式，一种是scp命令行拷贝  
> 另一种是iFunBox工具操作  

我这里采用的是第一种scp命令行  
 
```  
LeonLei-MBP:~ gaoshilei$ scp /Users/gaoshilei/Desktop/reverse/dumpdecrypted/dumpdecrypted.dylib   root@192.168.0.115:/var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents  
dumpdecrypted.dylib                                                              100%  193KB 192.9KB/s   00:00 
```  

我们已经将dumpdecrypted.dylib拷贝到了微信沙盒的Document目录中，可以砸壳了：  
  
```  
iPhone-5S:~ root# cd /var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents/
iPhone-5S:/var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents root# DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib /var/mobile/Containers/Bundle/Application/2A4313C7-6B36-40AF-9BEC-2C77FF1AC484/WeChat.app/WeChat
mach-o decryption dumper
DISCLAIMER: This tool is only meant for security research purposes, not for application crackers.
[+] detected 64bit ARM binary in memory.
[+] offset to cryptid found: @0x100024ca8(from 0x100024000) = ca8
[+] Found encrypted data at address 00004000 of length 45678592 bytes - type 1.
[+] Opening /private/var/mobile/Containers/Bundle/Application/2A4313C7-6B36-40AF-9BEC-2C77FF1AC484/WeChat.app/WeChat for reading.
[+] Reading header
[+] Detecting header type
[+] Executable is a plain MACH-O image
[+] Opening WeChat.decrypted for writing.
[+] Copying the not encrypted start of the file
[+] Dumping the decrypted data into the file
[+] Copying the not encrypted remainder of the file
[+] Setting the LC_ENCRYPTION_INFO->cryptid to 0 at offset ca8
[+] Closing original file
[+] Closing dump file
iPhone-5S:/var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents root#  
```
等待命令执行完，此时已经完成砸壳，我们看一下当前目录都有啥：  
  
```  
iPhone-5S:/var/mobile/Containers/Data/Application/B591D3D1-5B75-4F55-923B-C9FBF339EFE5/Documents root# ls -o
total 55272
drwxr-xr-x  6 mobile      272 Aug 26 13:48 00000000000000000000000000000000
drwxr-xr-x 20 mobile     1122 Oct 10 15:28 6f696a1b596ce2499419d844f90418aa
drwxr-xr-x  3 mobile      136 Oct  9 10:56 CrashReport
-rw-r--r--  1 mobile      310 Aug 26 13:49 Ksid
-rw-r--r--  1 mobile     1036 Oct 10 13:40 LocalInfo.lst
drwxr-xr-x  5 mobile      272 Aug 26 13:49 MMResourceMgr
drwxr-xr-x  2 mobile      748 Aug 26 13:51 MMappedKV
-rw-r--r--  1 mobile       15 Oct 10 13:40 SafeMode.dat
-rw-r--r--  1 root   56380816 Oct 10 15:37 WeChat.decrypted
-rwxr-xr-x  1 root     197528 Oct 10 15:34 dumpdecrypted.dylib
-rw-r--r--  1 mobile      448 Aug 26 13:49 mmupdateinfo.archive
```  
砸好壳的微信可执行文件`WeChat.decrypted`已经生成，现在就可以把文件拷到Mac上利用IDA或者Hopper的分析了。

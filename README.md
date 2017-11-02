# 前言
本文档主要用来记录自己搭建hexo博客的一些命令和过程，方便以后重装。  
下文的环境为 CentOS6.9  
## 安装依赖和相关服务  
###1、 安装 NodeJS 和 NPM

```shell
[root@California_VPS ~]# curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
```  

执行完这个命令之后就可以安装NodeJS  

```shell  
[root@California_VPS ~]# yum install -y nodejs
```  

这里安装的是8.X版本，如果安装其他版本将`setup_8.x`中的8改成对应的版本就可以了。  
安装完成之后执行命令检查安装结果：  

```shell  
[root@California_VPS ~]# node -v
v8.8.1
[root@California_VPS ~]# npm -v
5.4.2
```  

###2、安装 Nginx  
通过 yum方式安装比较麻烦，还需要安装epel依赖库，下面介绍一种最简单的安装方法 

```shell  
[root@California_VPS ~]# vim /etc/yum.repos.d/nginx.repo 
``` 
先在 yum.repos.d 文件下新建一个`nginx.repo`，然后将下面的内容拷贝进去，`:wq`保存退出

```shell  
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=0
enabled=1 
```  

执行下面的命令直接从配置文件安装 nginx

```shell  
[root@California_VPS ~]# yum install nginx -y
```  

然后打开服务器所在的IP测试nginx是否安装完成。


###3、安装 Hexo
按照官网的文档执行命令  

```shell  
[root@California_VPS ~]# npm install -g hexo-cli
```  

顺利的话一会就安装好了，有时候会遇到 npm 权限问题  

```shell  
/usr/bin/hexo -> /usr/lib/node_modules/hexo-cli/bin/hexo

> hexo-util@0.6.1 postinstall /usr/lib/node_modules/hexo-cli/node_modules/hexo-util
> npm run build:highlight


> hexo-util@0.6.1 build:highlight /usr/lib/node_modules/hexo-cli/node_modules/hexo-util
> node scripts/build_highlight_alias.js > highlight_alias.json

sh: highlight_alias.json: 权限不够
npm ERR! code ELIFECYCLE
npm ERR! errno 1
npm ERR! hexo-util@0.6.1 build:highlight: `node scripts/build_highlight_alias.js > highlight_alias.json`
npm ERR! Exit status 1
npm ERR! 
npm ERR! Failed at the hexo-util@0.6.1 build:highlight script.
npm ERR! This is probably not a problem with npm. There is likely additional logging output above.  
```  

这个时候需要开启 npm 的 unsafe-perm 模式  

```shell  
[root@California_VPS ~]# npm config set unsafe-perm "true"  
```  

查看是否设置成功  

```shell  
[root@California_VPS ~]# npm config get unsafe-perm
true
```  

如果为 `true` 则设置成功，再次执行 hexo 的安装命令即可顺利安装成功。  

因为需要把之前在 github 的博客备份重新拷贝新的服务器上，所以要配置 ssh 公钥方便 git 操作。

先生成公钥

```shell 
[root@California_VPS ~]# ssh-keygen -t rsa -b 4096 -C "xxxxx@xxx.com"  
```  

这一步会生成ssh公钥，也就是 public key，生成之后可以通过下面的命令查看  

```shell  
ls -al ~/.ssh
```  

如果有 `id_rsa` `id_rsa.pub` 证明生成成功，然后通过下面的命令查看 ssh 公钥

```shell  
cat ~/.ssh/id_rsa.pub
```  
再将这个公钥拷贝到 github 的账户配置中即可。   

###4、配置博客  

从 github 上把之前的博客 clone 下来，放到 root 目录下：  

```shell  
git clone https://github.com/xiangming/landscape-plus.git  
``` 

然后配置 nginx，让 80 端口指向博客静态页面首页，在 nginx 配置文件目中新建一个`hexo.conf`文件 

```shell  
[root@California_VPS ~]# vim /etc/nginx/conf.d/hexo.conf  
```  

写入相应的配置  

```shell  
server {
    listen          80;
    server_name     gaoshilei.com www.gaoshilei.com;
    location / {
        root        /root/hexo-blog/public;
        index       index.html;
    }
}
```  

重启 nginx 使服务生效  

```shell  
[root@California_VPS ~]# nginx -s reload
```  

此时去访问 IP 得到的是一个 404 报错，因为 nginx 是以 nginx 用户运行的，他没有博客目录的读写权限，有两个方法可以解决：  
1. 给博客目录赋权，让 nginx 用户拥有读写权限
2. 让 nginx 以 root 用户运行 

我采用第二种方式，修改 nginx 的配置文件  

```shell  
[root@California_VPS ~]# vim /etc/nginx/nginx.conf  
```  

将 `user  nginx;` 改成 `user  root;` 即可。然后重启 nginx。  

再去访问发现 404 没了，但是页面是一片空白，找了半天原因，之前用到的主题并没有上传到 github 上，将主题拷贝到 `themes` 文件夹下，然后部署 hexo 就可以正常访问了。  

**hexo 常用的命令**  
生成静态文件并部署网站:

```  
# hexo generate -d
```  

清除缓存文件 (db.json) 和已生成的静态文件 (public)  

```  
# hexo clean  
```  

生成站点map  

```  
# npm install hexo-generator-sitemap --save
# npm install hexo-generator-baidu-sitemap --save  
```  

###5、全站 HTTPS 
使用 Let’s Encrypt 的免费证书，不过每三个月要续签一次，安装可以通过 Certbot 的傻瓜式操作  

```shell  
[root@California_VPS www]# wget https://dl.eff.org/certbot-auto
[root@California_VPS www]# chmod a+x certbot-auto  
``` 
下载脚本，然后赋权  

```shell  
[root@California_VPS www]# sudo ./certbot-auto --nginx
```  

执行脚本，获取证书，Certbot 会自动帮我们配置 nginx 的一些配置。走到最后可能遇到这种情况  

>  
Cannot find a VirtualHost matching domain www.gaoshilei.com. In order for Certbot to correctly perform the challenge please add a corresponding server_name directive to your nginx configuration: https://nginx.org/en/docs/http/server_names.html

之前在配置 nginx.conf 文件的时候忘记加域名了，把 server_name 补全就行了，然后重新执行一次脚本，顺利申请了证书，而且 Certbot 都帮我配置好了，nice！  
不过这个证书有效期只有三个月，所以需要续签，可以手动续签，证书快过期的时候执行  

```shell  
# sudo /root/www/certbot-auto renew
```

或者将上面的命令加入 `crontab` 定时任务  

```shell  
[root@California_VPS etc]# ps -ef | grep cron
root      1164     1  0 Oct30 ?        00:00:00 crond
root      8507  8222  0 07:31 pts/0    00:00:00 grep cron  
[root@California_VPS etc]# service crond status
crond (pid  1164) is running...
```  

先检查一下有没有安装 crontab，并且查看 crontab 的运行状态。最后配置  

```shell  
[root@California_VPS etc]# crontab -e
```

添加下面这条命令到配置文件中

```shell  
0 0 * * 0 /root/www/certbot-auto renew  
```

这条命令的意思是每周日的0点0分执行`/root/www/certbot-auto renew`这条命令。执行下面这条命令查看定时任务列表中是否有刚才添加的任务

```shell  
[root@California_VPS etc]# crontab -l 
0 0 * * 0 /root/www/certbot-auto renew
```












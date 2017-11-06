---
title: 快速搭建Hexo博客+webhook自动部署+全站HTTPS  
date: 2017-10-30 19:09:00  
categories:  
- 备忘录  
tags:  
- 个人博客  
permalink: hexo-init  
---

本文档主要用来记录自己借助[Hexo](https://hexo.io)搭建博客的一些步骤和命令，方便以后重装；新人也可以通过此篇文章快速搭建自己的个人博客。
下文的环境为:  
VPS： CentOS 6.9
本地： MacOS  

## 搭建博客
### 1、安装 NodeJS 和 NPM  

```shell  
[root@California_VPS ~]# curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -  
```

执行完这个命令之后就可以安装NodeJS  

```shell  
[root@California_VPS ~]# yum install -y nodejs
```

<!-- more -->

这里安装的是8.X版本，如果安装其他版本将`setup_8.x`中的8改成对应的版本就可以了。  
安装完成之后执行命令检查安装结果：  

```shell  
[root@California_VPS ~]# node -v
v8.8.1
[root@California_VPS ~]# npm -v
5.4.2
```

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)  

### 2、安装 Nginx  
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


### 3、安装 Hexo
按照官网的文档执行命令  

```shell  
[root@California_VPS ~]# npm install -g hexo-cli
```

顺利的话一会就安装好了，有时候会遇到 npm 权限问题  

  
> /usr/bin/hexo -> /usr/lib/node_modules/hexo-cli/bin/hexo
hexo-util@0.6.1 postinstall /usr/lib/node_modules/hexo-cli/node_modules/hexo-util
npm run build:highlight
hexo-util@0.6.1 build:highlight /usr/lib/node_modules/hexo-cli/node_modules/hexo-util
node scripts/build_highlight_alias.js > highlight_alias.json
sh: highlight_alias.json: 权限不够
npm ERR! code ELIFECYCLE
npm ERR! errno 1
npm ERR! hexo-util@0.6.1 build:highlight: `node scripts/build_highlight_alias.js > highlight_alias.json`
npm ERR! Exit status 1
npm ERR! 
npm ERR! Failed at the hexo-util@0.6.1 build:highlight script.
npm ERR! This is probably not a problem with npm. There is likely additional logging output above.  


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

**注意：  为了方便在本地修改博客、实时预览、自动部署，以上（除了Nginx安装）所有步骤在本地机器上也需要重新操作一遍，以后在本地直接修改之后推送github，配合下文的webhook，服务器会自动更新**  

### 4、配置博客  

新安装：参照 [Hexo官方教程](https://hexo.io/zh-cn/docs/setup.html) 
重装：从 github 上把之前的博客 clone 下来，放到 root 目录下：  

```shell  
git clone git@github.com:gaoshilei/hexo-blog.git  
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

安装 hexo 服务（本地可以通过这个服务实现预览，不需要安装nginx）

```  
# npm install hexo-server --save  
```

启动 hexo 服务，默认端口为 4000

``` 
# hexo server
```

用指定端口(port)启动启动 hexo 服务

```
# hexo server -p port
```

生成静态文件

```  
# hexo g
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


## 配置 webhooks 自动更新博客  
每次在本地更新了博客，push 到 github 上，还要去 VPS 再 git pull 一下，确实很麻烦，配置好 webhooks 就可以在 github 有 push 操作时自动更新并部署博客。  

webhooks 在 github 对应仓库直接设置就行，重点是服务器的接收和相应的操作。  
有 Python、PHP、NodeJS 多种方式可以接收 webhooks , 由于 hexo 是基于 NodeJS 的，所以这里用 NodeJS 来接收 github 的 push 事件。 

安装依赖库 `github-webhook-handler`：  

```shell  
[root@California_VPS ~]# npm install -g github-webhook-handler
```

安装完成之后配置 `webhooks.js`  

```shell  
[root@California_VPS hexo-blog]# vim webhooks.js 
```

然后将下面代码的拷贝进去  

```js   
var http = require('http')
var createHandler = require('github-webhook-handler')
var handler = createHandler({ path: '/webhooks_push', secret: 'leonlei1226' })
// 上面的 secret 保持和 GitHub 后台设置的一致

function run_cmd(cmd, args, callback) {
  var spawn = require('child_process').spawn;
  var child = spawn(cmd, args);
  var resp = "";

  child.stdout.on('data', function(buffer) { resp += buffer.toString(); });
  child.stdout.on('end', function() { callback (resp) });
}

http.createServer(function (req, res) {
  handler(req, res, function (err) {
    res.statusCode = 404
    res.end('no such location')
  })
}).listen(6666)

handler.on('error', function (err) {
  console.error('Error:', err.message)
})

handler.on('push', function (event) {
  console.log('Received a push event for %s to %s',
    event.payload.repository.name,
    event.payload.ref);
    run_cmd('sh', ['./deploy.sh'], function(text){ console.log(text) });
})
```

其中 **secret** 要和 github 仓库中 webhooks 设置的一致，**6666** 是监听端口可以随便改，不要冲突就行，**./deploy.sh** 是接收到 push 事件时需要执行的shell脚本，与 `webhooks.js` 都存放在博客目录下；**path: '/webhooks_push** 是 github 通知服务器的地址，完整的地址是这样的`http://www.gaoshilei.com:6666/webhooks_push`  

> 用 https 会报错，github 设置页面会 deliver error，所以把地址改成了 http


配置`./deploy.sh`  

```shell  
[root@California_VPS hexo-blog]# vim deploy.sh
```

将下面代码拷贝进去

```shell  
git pull origin master
hexo g
```

然后运行  

```shell  
[root@California_VPS hexo-blog]# node webhooks.js 
```

就可以实现本地更新 push 到 github ，服务器会自动更新部署博客。  
最后要将进程加入守护，通过 pm2 来实现  

```shell  
[root@California_VPS ~]# npm install pm2 --global
```

然后通过 pm2 启动 `webhooks.js`  

```shell  
[root@California_VPS hexo-blog]# pm2 start webhooks.js 
[PM2] Starting /root/hexo-blog/webhooks.js in fork_mode (1 instance)
[PM2] Done.
┌──────────┬────┬──────┬───────┬────────┬─────────┬────────┬─────┬───────────┬──────┬──────────┐
│ App name │ id │ mode │ pid   │ status │ restart │ uptime │ cpu │ mem       │ user │ watching │
├──────────┼────┼──────┼───────┼────────┼─────────┼────────┼─────┼───────────┼──────┼──────────┤
│ webhooks │ 0  │ fork │ 10010 │ online │ 0       │ 0s     │ 14% │ 24.2 MB   │ root │ disabled │
└──────────┴────┴──────┴───────┴────────┴─────────┴────────┴─────┴───────────┴──────┴──────────┘
 Use `pm2 show <id|name>` to get more details about an app  
```

## 全站 HTTPS 
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

大功告成！


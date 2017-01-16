---
title: 你真的会用strong-weak dance吗？
date: 2017-01-16 15:34:45
categories:  
- 技术笔记
tags: 
- block  
- retain cycle   
permalink: strong-weak_dance

---


>	下文的讨论基于ARC  


平时开发中我们遇到block里面引用self的情况，大部分都是这样处理的  

```ObjC  
    __weak typeof(self) weakSelf = self;
    self.myBlock =  ^{
    __strong typeof(self) strongSelf = weakSelf;
        [strongSelf doSomething]; 
        [strongSelf doSomethingElse]; 
    };  
```


我们习惯了这样用，**貌似这样用了之后可以解决循环引用的问题，而且可以保证block执行之前self不会被释放掉？真相总是残酷的，然而事实并非如此！**下面将会对block中引用self的三种方式进行讨论，并给出原因和另外一种解决方案。

<!-- more -->

##	1.  block中直接引用self  

这种情况使用是block被没有被self强引用，因此这样不会导致retain cycle。  

```ObjC
    dispatch_block_t completionHandler = ^{
        NSLog(@"%@", self);
    }  
```

##	2.在block外部创建weakself变量，在block中引用weakself  

当block被self强引用，此时如果在block内强引用self将会导致retain cycle。所以我们就想到了在block外部创建一个weakself，然后block在创建的时候捕获到的是weakself，这样就不会导致retain cycle。  

```ObjC  
__weak typeof(self) weakSelf = self;
dispatch_block_t block =  ^{
    [weakSelf doSomething]; 
    [weakSelf doSomethingElse]; 
};  
```

但是要注意的是block捕获的是weakself变量，如果在执行doSomething的过程中self被释放掉，由于是弱引用，weakself也将置空，下面的doSomethingElse是无法得到执行的，看一个例子：

下面的例子展示的是，在block调用之后的1秒后释放self，在block中调用doSomething，2秒之后再调用doAnotherThing，意味着调用doAnotherThing之前self已经被释放了  


```ObjC  

//viewController.m
- (void)viewDidLoad {
    [super viewDidLoad];
    self.sself = [strongweakself new];
    [self.sself test];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        NSLog(@"self.block被释放!");
        self.sself = nil;
    });
}
//strongweakself.m
-(void)test
{
    self.myobject = [TestObject new];
    __weak typeof(self) __weakself = self;
    [self.myobject setWeakblock:^{
        NSLog(@"调用block!");
        [__weakself doSomething];
            dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
                [__weakself doAnotherThing];
            });
    }];
    self.myobject.weakblock();
}
-(void)doSomething
{
    NSLog(@"%s",__func__);
}
-(void)doAnotherThing
{
    NSLog(@"%s",__func__);
}
-(void)dealloc{
    NSLog(@"%s",__func__);
}
```


从打印日志可以看出，block执行大约1秒之后self被dealloc，doAnotherThing并没有得到调用

```ObjC 
2017-01-16 14:31:13.834 strong-weak dance[11366:4727954] 调用block!
2017-01-16 14:31:13.836 strong-weak dance[11366:4727954] -[strongweakself doSomething]
2017-01-16 14:31:14.893 strong-weak dance[11366:4727954] self.block被释放!
2017-01-16 14:31:14.893 strong-weak dance[11366:4727954] -[strongweakself dealloc]
```

所以只使用weakself，在self被释放之后，weakself由于self的释放已经为空，后面的self都将失效，所以在block中这样引用self是非常危险的，下面就要谈谈我们最熟悉的strong-weak dance了。

##	3.strong-weak dance  

对比第二种方案我们看一下doAnotherThing是否可以得到调用，稍微改一下代码，还是在block执行1秒后释放self，我们看看后面的self引用是否有效

```ObjC 
-(void)test
{
    self.myobject = [TestObject new];
    __weak typeof(self) __weakself = self;
    [self.myobject setWeakblock:^{
        NSLog(@"调用block!");
        __strong typeof(self) __strongself= __weakself;
        [__strongself doSomething];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            [__strongself doAnotherThing];
        });
    }];
    self.myobject.weakblock();
}
```

此时看打印日志：

```ObjC
2017-01-16 14:36:39.039 strong-weak dance[11374:4728878] 调用block!
2017-01-16 14:36:39.039 strong-weak dance[11374:4728878] -[strongweakself doSomething]
2017-01-16 14:36:40.110 strong-weak dance[11374:4728878] self.block被释放!
2017-01-16 14:36:41.213 strong-weak dance[11374:4728878] -[strongweakself doAnotherThing]
2017-01-16 14:36:41.213 strong-weak dance[11374:4728878] -[strongweakself dealloc]
```


虽然self被释放掉了，但是并没有dealloc，因为block内部的strongself对他进行了一次retain，当doAnotherThing执行完毕，strongself对他的引用计数减一，self被dealloc彻底销毁。

**那么问题来了！strong-weak dance能不能解决block执行前，self被释放的问题？**下面继续验证  
我们改一下代码，在1秒之后释放self，在2秒之后执行block（*注意延时block中对于self的处理是weakself，防止延时block对self进行retain影响验证结果*）

```ObjC
//viewController.m
- (void)viewDidLoad {
    [super viewDidLoad];
    self.sself = [strongweakself new];
    [self.sself test];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        NSLog(@"self.block被释放!");
        self.sself = nil;
    });
}

//strongweakself.m
-(void)test
{
    self.myobject = [TestObject new];
    __weak typeof(self) __weakself = self;
    [self.myobject setWeakblock:^{
    NSLog(@"调用block!");
    __strong typeof(self) __strongself= __weakself;
    [__strongself doSomething];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        [__strongself doAnotherThing];
    });
    }];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        NSLog(@"%@",__weakself);
        __weakself.myobject.weakblock();
});
}

```

看一下日志：

```ObjC
2017-01-16 14:44:26.314 strong-weak dance[11395:4730727] self.block被释放!
2017-01-16 14:44:26.314 strong-weak dance[11395:4730727] -[strongweakself dealloc]
2017-01-16 14:44:27.372 strong-weak dance[11395:4730727] (null)
```

当开始调用block的时候报错了，self这时已经被dealloc掉。strong-weak dance并没有解决这种问题。看到这心是不是凉了半截？真相就是如此，我们平时一直使用的strong-weak dance也只能解决block得到调用之后self不被释放的问题。  

这是我们最常用的是一种方案，因为block创建时捕获的是weakself，所以block执行之前不能够控制self的生命周期，所以这样不会导致整个block对self进行强引用。之后在block内部创建一个对self进行retain的变量strongself，**strongself 作为局部变量强引用了 self 并且会在block执行完毕的时候被自动销毁，这样既可以保证在block执行期间 self 不会被外界干掉，同时也解决了retain cycle的问题。**

##	总结  

通过上面几个小栗子可以看出来：strong-weak dance确实是比较好的解决方案，但是也不是万能的，他不能解决block调用之前self被释放的问题，下面将block中引用self分为4中场景：

####	1.	使用self  
当self不持有、不间接持有block时，可以在block内部直接引用self。

####	2.使用weakself
当self持有或间接持有block，可以通过在外部创建self的弱引用weakself然后捕获到block内部进行使用，但是这样使用存在一定风险，一般也不推荐使用。

####	3.使用strong-weak dance
当self持有或间接持有block，此时要使用strong-weak dance。
这种方法也不是万能的，在block被执行前，block对self依然只是弱引用，进入block里面才会retain一次，保证在block执行期间self都不会被释放掉。


####	4.	block中强引用self并且打破retain cycle
**不管是weakself还是strong-weak dance，目的都是避免retain cycle，strong-weak dance的本质也是在block中搞了一个局部变量来打破这种循环引用的；**    
如果我们在block中直接使用self，并且在适当的时机打破这种循环（比如说在block执行完成将这个block销毁）也可以避免retain cycle，并且这种在block创建时就强引用的方式，在block被调用前 self 不会被释放掉，可以弥补strong-weak dance的不足。

关于本文的内容可能存在不足的地方，欢迎大家指正！



##	参考资料
1.	[http://albertodebortoli.com/blog/2013/08/03/objective-c-blocks-caveat](http://albertodebortoli.com/blog/2013/08/03/objective-c-blocks-caveat)

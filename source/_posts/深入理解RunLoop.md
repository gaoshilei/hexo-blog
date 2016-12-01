---
title: 深入理解RunLoop
date: 2016-11-20 14:23:11
categories:  
- 技术笔记  
tags:  
- RunLoop  
- NSTimer  
- AutoreleasePool
- AFNetworking  
permalink: RunLoop  

---

#	一、	RunLoop初识  

日常的开发工作中，我们几乎很少注意RunLoop，因为我们基本上“用不到”RunLoop。包括我在内应该有很多人都不了解这个东西，只是听说过。最近有空查了不少资料终于把RunLoop运行原理搞清楚了。  
本文会对RunLoop的原理进行深入探讨，但是不涉及底层的实现。  
我们平时开发中的很多东西都和RunLoop相关，比如：  

-	AutoreleasePool   
-	NSTimer  
-	消息通知
-	perform函数
-	网络请求
-	dispatch调用
-	block回调
-	KVO
-	触摸事件以及各种硬件传感器 

RunLoop机制贯穿整个App的生命周期的，这里提前剧透个彩蛋：  
>	我们都知道：如果主线程的RunLoop挂掉了，App也就挂掉了 

转载请注明出处：[来自LeonLei的博客http://www.gaoshilei.com](http://www.gaoshilei.com)
**BUT：**  
我们通过RunLoop机制可以让崩溃的App继续保持运行，非常英吹思婷！后面会有介绍。  

#	二、	RunLoop详解   

计算机处理任务有进程和线程的概念，安卓中一个应用可以开启多个进程，而在iOS中一个App只能开启一个进程，但是线程可以开启多个。线程是用来处理事务的，多个线程处理事务是为了防止线程堵塞；一般来说一个线程一次只能执行一个任务，任务执行完成这个线程就会退出。  
某些情况下我们需要这个线程一直运行着，不管有没有任务执行（*比方说App的主线程*），所以需要一种机制来维持线程的生命周期，iOS中叫做RunLoop，安卓里面的Looper机制和此类似。  
为了让线程不退出随时候命处理事件而不退出，可以将逻辑简化为下面的代码  

```ObjC
do{
var message = getNewmessages();//接收来自外部的消息
exec(message);//处理消息任务
}while(0==isQuit)
```

RunLoop实际上也是一个对象，这个对象管理了线程内部需要处理的事件和消息，存在RunLoop的线程一直处于“消息接收->等待->处理”的循环中，直到这个循环结束（RunLoop被释放）。  

##	1.	进程、线程、RunLoop之间的关系 
**这里举一个比较通俗易懂的例子：** 

-	进程：工厂  
-	线程：流水线  
-	RunLoop：生产线上面的主管  

当工厂接到商家的订单时，会将订单生产的消息（外界的event消息）发送给对应流水线上的主管（RunLoop），主管接收到消息之后启动这个流水线（唤醒线程）进行生产（线程处理事务）。如果这个流水线没有主管，流水线将会被工厂销毁。  

需要注意的是，线程与RunLoop是一一对应的关系（对应关系保存在一个全局的Dictionary里），线程创建之后是没有RunLoop的（主线程除外），RunLoop的创建是发生在第一次获取时。  
>	苹果不允许直接创建RunLoop，但是可以通过[NSRunLoop currentRunLoop]或者CFRunLoopGetCurrent()来获取（如果没有就会自动创建一个）。

一般开发中使用的RunLoop就是NSRunLoop和CFRunLoopRef，CFRunLoopRef属于Core Foundation框架，提供的是C函数的API，**是线程安全的**，NSRunLoop是基于CFRunLoopRef的封装，提供了面向对象的API，**这些API不是线程安全的**。  

由于NSRunLoop是基于CFRunLoop封装的，下文关于RunLoop的原理讨论都会基于CFRunLoop来进行。NSRunLoop和CFRunLoop所有类都是一一对应的关系。

##	2.	RunLoop主要组成  
>	CFRunLoop对象可以检测某个task或者dispatch的输入事件，当检测到有输入源事件，CFRunLoop将会将其加入到线程中进行处理。比方说用户输入事件、网络连接事件、周期性或者延时事件、异步的回调等。  
>
>	RunLoop可以检测的事件类型一共有3种，分别是CFRunLoopSource、CFRunLoopTimer、CFRunLoopObserver。可以通过CFRunLoopAddSource, CFRunLoopAddTimer或者CFRunLoopAddObserver添加相应的事件类型。  
>
>	要让一个RunLoop跑起来还需要run loop modes，每一个source, timer和observer添加到RunLoop中时必须要与一个模式（CFRunLoopMode）相关联才可以运行。

上面是对于CFRunLoop官方文档的解释，大致说明了RunLoop的工作原理。  
RunLoop的主要组成部分如下：  

-	Run Loop （CFRunLoopRef）
-	Run Loop Source（CFRunLoopSourceRef）
-	Run Loop Timer（CFRunLoopTimerRef）
-	Run Loop Observer（CFRunLoopObserverRef）
-	Run Loop Modes（CFRunLoopModeRef）

RunLoop共包含5个类，但公开的只有Source、Timer、Observer相关的三个类。
这5个类之间的关系关系：  
![](http://oeat6c2zg.bkt.clouddn.com/RunLoop.png)

下面对这几个部分作详细的讲解。  

###	1.	RunLoop Modes  
>	Run Loop Mode就是流水线上能够生产的产品类型，流水线在一个时刻只能在一种模式下运行，生产某一类型的产品。消息事件就是订单。  

CFRunLoopMode 和 CFRunLoop的结构大致如下：

```ObjC
struct __CFRunLoopMode {
CFStringRef _name;            // Mode Name, 例如 @"kCFRunLoopDefaultMode"
CFMutableSetRef _sources0;    // Set
CFMutableSetRef _sources1;    // Set
CFMutableArrayRef _observers; // Array
CFMutableArrayRef _timers;    // Array
...
};

struct __CFRunLoop {
CFMutableSetRef _commonModes;     // Set
CFMutableSetRef _commonModeItems; // Set<Source/Observer/Timer>
CFRunLoopModeRef _currentMode;    // Current Runloop Mode
CFMutableSetRef _modes;           // Set
...
};
```

一个RunLoop包含了多个Mode，每个Mode又包含了若干个Source/Timer/Observer。每次调用 RunLoop的主函数时，只能指定其中一个Mode，这个Mode被称作CurrentMode。如果需要切换 Mode，只能退出Loop，再重新指定一个Mode进入。这样做主要是为了分隔开不同Mode中的Source/Timer/Observer，让其互不影响。下面是5种Mode  

-	**kCFDefaultRunLoopMode**	App的默认Mode，通常主线程是在这个Mode下运行
-	**UITrackingRunLoopMode**	界面跟踪Mode，用于ScrollView追踪触摸滑动，保证界面滑动时不受其他Mode影响
-	**UIInitializationRunLoopMode** 在刚启动App时第进入的第一个Mode，启动完成后就不再使用
-	**GSEventReceiveRunLoopMode**	接受系统事件的内部Mode，通常用不到
-	**kCFRunLoopCommonModes**	这是一个占位用的Mode，不是一种真正的Mode

其中kCFDefaultRunLoopMode、UITrackingRunLoopMode是苹果公开的，其余的mode都是无法添加的。既然没有CommonModes这个模式，那我们平时用的这行代码怎么解释呢？  


```
[[NSRunLoop mainRunLoop] addTimer:timer forMode:NSRunLoopCommonModes]; 
```

**什么是CommonModes？**   

一个 Mode 可以将自己标记为"Common"属性（通过将其 ModeName 添加到 RunLoop 的 "commonModes" 中）。每当 RunLoop 的内容发生变化时，RunLoop 都会自动将 _commonModeItems 里的 Source/Observer/Timer 同步到具有 "Common" 标记的所有Mode里
主线程的 RunLoop 里有 kCFRunLoopDefaultMode 和 UITrackingRunLoopMode，这两个Mode都已经被标记为"Common"属性。当你创建一个Timer并加到DefaultMode时，Timer会得到重复回调，但此时滑动一个 scrollView 时，RunLoop 会将 mode 切换为TrackingRunLoopMode，这时Timer就不会被回调，并且也不会影响到滑动操作。    
如果想让scrollView滑动时Timer可以正常调用，一种办法就是手动将这个 Timer 分别加入这两个 Mode。另一种方法就是将 Timer 加入到CommonMode 中。

**怎么将事件加入到CommonMode？**  
我们调用上面的代码将 Timer 加入到CommonMode 时，但实际并没有 CommonMode，其实系统将这个 Timer 加入到顶层的 RunLoop 的 commonModeItems 中。commonModeItems 会被 RunLoop 自动更新到所有具有"Common"属性的 Mode 里去。  
这一步其实是系统帮我们将Timer加到了kCFRunLoopDefaultMode和UITrackingRunLoopMode中。  

###	2.	RunLoop Source  
CFRunLoopSourceRef是事件源（输入源），比如外部的触摸，点击事件和系统内部进程间的通信等。  
按照官方文档，Source的分类：

-	Port-Based Sources
-	Custom Input Sources
-	Cocoa Perform Selector Sources

Source有两个版本：Source0 和 Source1（*这么风骚的名字不知道是谁想出来的*）。 
**Source0：**	非基于Port的，只包含了一个回调（函数指针），它并不能主动触发事件。使用时，你需要先调用 CFRunLoopSourceSignal(source)，将这个 Source 标记为待处理，然后手动调用 CFRunLoopWakeUp(runloop) 来唤醒 RunLoop，让其处理这个事件。  
**Source1：**	基于Port的，包含了一个 mach_port 和一个回调（函数指针），被用于通过内核和其他线程相互发送消息。这种 Source 能主动唤醒 RunLoop 的线程。后面讲到的AFNetwoeking创建常驻线程就是在线程中添加一个NSport来实现的。

###	3.	RunLoop Timer  
CFRunLoopTimerRef是基于时间的触发器，基本上说的就是NSTimer，它受RunLoop的Mode影响（GCD的定时器不受RunLoop的Mode影响），当其加入到 RunLoop 时，RunLoop会注册对应的时间点，当时间点到时，RunLoop会被唤醒以执行那个回调。如果线程阻塞或者不在这个Mode下，触发点将不会执行，一直等到下一个周期时间点触发。

###	4.	RunLoop Observer 
CFRunLoopObserverRef 是观察者，每个 Observer 都包含了一个回调（函数指针），当 RunLoop 的状态发生变化时，观察者就能通过回调接受到这个变化。可以观测的时间点有以下几个

```ObjC
enum CFRunLoopActivity {
kCFRunLoopEntry                     = (1 << 0),    // 即将进入Loop   
kCFRunLoopBeforeTimers 		= (1 << 1),    // 即将处理 Timer    	
kCFRunLoopBeforeSources		= (1 << 2),    // 即将处理 Source  
kCFRunLoopBeforeWaiting		= (1 << 5),    // 即将进入休眠     
kCFRunLoopAfterWaiting 		= (1 << 6),    // 刚从休眠中唤醒   
kCFRunLoopExit                      = (1 << 7),    // 即将退出Loop  
kCFRunLoopAllActivities		= 0x0FFFFFFFU  // 包含上面所有状态  
};
typedef enum CFRunLoopActivity CFRunLoopActivity;
```

##	3.	RunLoop 运行机制  
这是我从别人博客上面摘录的一张图片，详细的描述了RunLoop运行机制  
![](http://oeat6c2zg.bkt.clouddn.com/RunLoop_1.png)  

每次线程运行RunLoop都会自动处理之前未处理的消息，并且将消息发送给观察者，让事件得到执行。RunLoop运行时首先根据modeName找到对应mode，如果mode里没有source/timer/observer，直接返回。   
**流程如下：**  

**Step1**  通知观察者 RunLoop 启动（之后调用内部函数，进入Loop，下面的流程都在Loop内部do-while函数中执行）   
**Step2**  通知观察者: RunLoop 即将触发 Timer 回调。（kCFRunLoopBeforeTimers）   
**Step3**  通知观察者: RunLoop 即将触发 Source0 回调。（kCFRunLoopBeforeSources）  
**Step4**  RunLoop 触发 Source0 回调。
**Step5** 	如果有 Source1 处于等待状态，直接处理这个 Source1 然后跳转到第9步处理消息。  
**Step6**	通知观察者：RunLoop 的线程即将进入休眠(sleep)。（kCFRunLoopBeforeWaiting）  
**Step7**	调用 `mach_msg` 等待接受 `mach_port` 的消息。线程将进入休眠, 直到被下面某一个事件唤醒  

>   1.	存在Source0被标记为待处理，系统调用CFRunLoopWakeUp唤醒线程处理事件  
>   2.	定时器时间到了   
>   3.	RunLoop自身的超时时间到了  
>   4.	RunLoop外部调用者唤醒      

**Step8**	通知观察者线程已经被唤醒 （kCFRunLoopAfterWaiting）  
**Step9**   处理事件  

>   1.	如果一个 Timer 到时间了，触发这个Timer的回调    
>   2.	如果有dispatch到main_queue的block，执行block   
>   3.	如果一个 Source1 发出事件了，处理这个事件   

**事件处理完成进行判断：**  

>   1.  进入loop时传入参数指明处理完事件就返回（stopAfterHandle）  
>   2.  超出传入参数标记的超时时间（timeout）  
>   3.  被外部调用者强制停止`__CFRunLoopIsStopped(runloop)`   
>   4.  source/timer/observer 全都空了`__CFRunLoopModeIsEmpty(runloop, currentMode)`  

上面4个条件都不满足，即没超时、mode里没空、loop也没被停止，那继续loop。此时跳转到步骤2继续循环。  

**Step10**	系统通知观察者: RunLoop 即将退出。
满足步骤9事件处理完成判断4条中的任何一条，跳出do-while函数的内部，通知观察者Loop结束。

#	三、	RunLoop实际应用  

##	1. AutoreleasePool  

App启动之后，系统启动主线程并创建了RunLoop，在 main thread 中注册了两个 observer ，回调都是`_wrapRunLoopWithAutoreleasePoolHandler()`  

###	1.	第一个observer  
监听了一个事件：  
####	1.	即将进入Loop（kCFRunLoopEntry）
其回调会调用 `_objc_autoreleasePoolPush()` 创建一个栈自动释放池，这个优先级最高，保证创建释放池在其他操作之前。  
###	2.	第二个observer
监听了两个事件：
####	1.	准备进入休眠（kCFRunLoopBeforeWaiting）
此时调用 `_objc_autoreleasePoolPop()` 和 `_objc_autoreleasePoolPush()` 来释放旧的池并创建新的池。  
####	2. 即将退出Loop（kCFRunLoopExit）
此时调用 `_objc_autoreleasePoolPop()`释放自动释放池。这个 observer 的优先级最低，确保池子释放在所有回调之后。  

在主线程中执行代码一般都是写在事件回调或Timer回调中的，这些回调都被加入了main thread的自动释放池中，所以在ARC模式下我们不用关心对象什么时候释放，也不用去创建和管理pool。（如果事件不在主线程中要注意创建自动释放池，否则可能会出现内存泄漏）。  

##	2.		事件响应  
系统注册了一个 Source1 用来接收系统事件，其回调函数为 `__IOHIDEventSystemClientQueueCallback()`。当一个硬件事件(触摸/锁屏/摇晃等)发生后，首先由 IOKit.framework 生成一个 IOHIDEvent 事件并由 SpringBoard 接收，

>	SpringBoard 只接收按键(锁屏/静音等)、触摸、加速，传感器等几种事件  

随后用 mach port 转发给需要的App进程。随后系统注册的那个 Source1 就会触发回调，并调用 `_UIApplicationHandleEventQueue()`进行应用内部的分发。
`_UIApplicationHandleEventQueue()` 会把 IOHIDEvent 事件处理并包装成 UIEvent 进行处理或分发，其中包括识别 UIGesture/处理屏幕旋转/发送给 UIWindow 等。通常事件比如 UIButton 点击、touchesBegin/Move/End/Cancel 事件都是在这个回调中完成的。    


##	3.		定时器  
###	1.	NSTimer 的工作原理
这里说的定时器就是NSTimer，我们使用频率最高的定时器，它的原型是CFRunLoopTimerRef。一个Timer注册 RunLoop 之后，RunLoop 会为这个Timer的重复时间点注册好事件。  
需要注意：  
>	1.	如果某个重复的时间点由于线程阻塞或者其他原因错过了，这个时间点会跳过去，直到下一个可以执行的时间点才会触发事件。举个栗子：假如公交车的发车间隔是10分钟，10:10的公交车我们没赶上，只能等10:20，如果由于我打电话没注意错过了10:20的车，只能等10:30的。  
>
>	2.	我们在哪个线程调用 NSTimer 就必须在哪个线程终止  

NSTimer有一个 tolerance ，官方文档给它的解释是 Timer 的计时并不是准确的，有一定的误差，这个误差就是 tolerance 默认为0，我们可以手动设置这个误差。文档最后还强调了，为了防止时间点偏移，系统有权力给这个属性设置一个值无论你设置的值是多少，即使RunLoop 模式正确，当前线程并不阻塞，系统依然可能会在 NSTimer 上加上很小的的容差。    

###	2.	NSTimer 优化使用  
我们在平时开发中一个很常见的现象：

>	在界面上有一个UIscrollview控件（tableview，collectionview等），如果此时还有一个定时器在执行一个事件，你会发现当你滚动scrollview的时候，定时器会失效。

这是因为，为了更好的用户体验，在主线程中UITrackingRunLoopMode的优先级最高。在用户拖动控件时，主线程的Run Loop是运行在UITrackingRunLoopMode下，而创建的Timer是默认关联为Default Mode，因此系统不会立即执行Default Mode下接收的事件。  

解决方法1：  
将当前 Timer 加入到 UITrackingRunLoopMode 或 kCFRunLoopCommonModes 中

```ObjC
NSTimer * timer = [NSTimer scheduledTimerWithTimeInterval:1.0 target:self selector:@selector(TimerFire:) userInfo:nil repeats:YES];
[[NSRunLoop mainRunLoop] addTimer:timer forMode:NSRunLoopCommonModes];  
// 或 [[NSRunLoop currentRunLoop] addTimer:timer forMode:UITrackingRunLoopMode];
[timer fire];
```
解决方法2：
因为GCD创建的定时器不受RunLoop的影响，可以使用GCD创建的定时器 

```ObjC
	//dispatch_source_t必须是全局或static变量，否则timer不会触发
    static dispatch_source_t timer;
    //创建新的调度源（这里传入的是DISPATCH_SOURCE_TYPE_TIMER，创建的是Timer调度
    timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, dispatch_get_main_queue());
    dispatch_source_set_timer(timer, DISPATCH_TIME_NOW, 1 * NSEC_PER_SEC, 0 * NSEC_PER_SEC);
    dispatch_source_set_event_handler(timer, ^{
        NSLog(@"%@",[NSThread currentThread]);
    });
    //启动或继续定时器
    dispatch_resume(timer);
```
###	3.	基于mode的拓展应用  
在 Timer 使用中我们可以通过将其加入到不同的mode来解决 Timer 的跳票问题。不过有些情况下，例如：  
>	用户滑动 scrollView 的过程中加载图片，由于UI的操作都是在主线程进行的，会造成滑动不流畅的问题，这个时候我们就需要在滑动的时候不加载图片，等滑动操作完成再进行加载图片的操作。  

一般我们可以设置代理，当用户滑动结束的时候通知代理加载图片，这样比较麻烦太low，基于RunLoop的原理我们只要一行代码即可搞定  

```ObjC
UIImage *downloadImage = ...
[self.imageView performSelector:@selector(setImage:) 
						withObject: downloadImage 
						afterDelay:3.0 
						inModes:@[NSDefaultRunLoopMode]];
```
通过将图片的设置 `setImage:` 添加到 DefaultMode 里面，确保在 UITrackingRunLoopMode 下该操作不会被执行，保证了滑动的流畅性。  

##	4.	网络请求

###	1.	网络请求接口
iOS中的网络请求接口自下而上有这么几层  
![](http://oeat6c2zg.bkt.clouddn.com/runloop-nsnetwork.png)  

**CFSocket** 是最底层的接口，只负责 socket 通信。  
**CFNetwork** 是基于 CFSocket 等接口的上层封装，ASIHttpRequest 工作在这层。  
**NSURLConnection** 是基于 CFNetwork 更高层的封装，提供了面向对象的接口，AFNetworking 工作在这一层。  
**NSURLSession** 看似是和 NSURLConnection 并列的，实际上它也用到了 NSURLConnection 的部分功能(比如 com.apple.NSURLConnectionLoader 线程)

开始网络传输时，NSURLConnection 创建了两个新线程：`com.apple.NSURLConnectionLoader` 和 `com.apple.CFSocket.private`。   
其中 CFSocket 线程是处理底层 socket 连接的，NSURLConnectionLoader 这个线程的RunLoop 创建了一个 Source1 事件源用来监听底层 socket 事件。当 CFSocket 处理好 socket 事件之后会通过 mach port 通知 NSURLConnectionLoader，然后 NSURLConnectionLoader 所在的线程再将消息通过 mach prot 转发给上层的 Delegate 所在的线程，同时唤醒 Delegate 线程的 RunLoop 来让其处理这些通知。  

###	2.	AFNetworking 的工作原理  
在AFNetworking2.6.3版本之前是有 AFURLConnectionOperation 这个类的，
AFNetworking 3.0 版本开始已经移除了这个类，AFN没有自己创建线程，而是采用的下面的这种方式  

```ObjC
[inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
[outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];  

SCNetworkReachabilityUnscheduleFromRunLoop(self.networkReachability, CFRunLoopGetMain(), kCFRunLoopCommonModes);
```

由于本文讨论的是RunLoop，所以这里我们还是回到2.6.3版本AFN自己创建线程并添加RunLoop的这种方式讨论，在 AFURLConnectionOperation 类中可以找到下面的代码  

```ObjC
+ (void)networkRequestThreadEntryPoint:(id)__unused object {
    @autoreleasepool {
        [[NSThread currentThread] setName:@"AFNetworking"];
        NSRunLoop *runLoop = [NSRunLoop currentRunLoop];
        [runLoop addPort:[NSMachPort port] forMode:NSDefaultRunLoopMode];
        [runLoop run];
    }
}

+ (NSThread *)networkRequestThread {
    static NSThread *_networkRequestThread = nil;
    static dispatch_once_t oncePredicate;
    dispatch_once(&oncePredicate, ^{
        _networkRequestThread = [[NSThread alloc] initWithTarget:self selector:@selector(networkRequestThreadEntryPoint:) object:nil];
        [_networkRequestThread start];
    });

    return _networkRequestThread;
}
```
从上面的代码可以看出，AFN创建了一个新的线程命名为 AFNetworking ，然后在这个线程中创建了一个 RunLoop ，在上面2.3章节 RunLoop 运行机制中提到了，一个RunLoop中如果source/timer/observer 都为空则会退出，并不进入循环。所以，AFN在这里为 RunLoop 添加了一个 NSMachPort ，这个port开启相当于添加了一个Source1事件源，但是这个事件源并没有真正的监听什么东西，只是为了不让 RunLoop 退出。 

```ObjC
//开始请求
- (void)start {
    [self.lock lock];
    if ([self isCancelled]) {
        [self performSelector:@selector(cancelConnection) onThread:[[self class] networkRequestThread] withObject:nil waitUntilDone:NO modes:[self.runLoopModes allObjects]];
    } else if ([self isReady]) {
        self.state = AFOperationExecutingState;
        [self performSelector:@selector(operationDidStart) onThread:[[self class] networkRequestThread] withObject:nil waitUntilDone:NO modes:[self.runLoopModes allObjects]];
    }
    [self.lock unlock];
}
//暂停请求
- (void)pause {
    if ([self isPaused] || [self isFinished] || [self isCancelled]) {
        return;
    }
    [self.lock lock];
    if ([self isExecuting]) {
        [self performSelector:@selector(operationDidPause) onThread:[[self class] networkRequestThread] withObject:nil waitUntilDone:NO modes:[self.runLoopModes allObjects]];

        dispatch_async(dispatch_get_main_queue(), ^{
            NSNotificationCenter *notificationCenter = [NSNotificationCenter defaultCenter];
            [notificationCenter postNotificationName:AFNetworkingOperationDidFinishNotification object:self];
        });
    }
    self.state = AFOperationPausedState;
    [self.lock unlock];
}
//取消请求
- (void)cancel {
    [self.lock lock];
    if (![self isFinished] && ![self isCancelled]) {
        [super cancel];
        if ([self isExecuting]) {
            [self performSelector:@selector(cancelConnection) onThread:[[self class] networkRequestThread] withObject:nil waitUntilDone:NO modes:[self.runLoopModes allObjects]];
        }
    }
    [self.lock unlock];
}
```

可以看到，AFN每次进行的网络操作，开始、暂停、取消操作时都将相应的执行任务扔进了自己创建的线程的 RunLoop 中进行处理，从而避免造成主线程的阻塞。  

##	5.	处理崩溃让程序继续运行  
我们都知道，如果App运行遇到 Exception 就会直接崩溃并且退出，其实真正让应用退出的并不是产生的异常，而是当产生异常时，系统会结束掉当前主线程的 RunLoop ，RunLoop 退出主线程就退出了，所以应用才会退出。明白这个道理，去完成这个“不可能的任务”就很简单了。  

接下来我们就去让应用在崩溃时依然可以正常运行，这个是非常有意义的。  

###	1.	提升用户体验	  
应用遇到BUG崩溃时一般会给使用者造成非常不好的用户体验，如果当应用崩溃时我们让用户选择退出还是继续运行，那么用户会感觉我们的App跟别人的不一样，叼叼哒！

###	2.	收集崩溃日志
苹果提供了产生 Exception 的处理方法，我们可以在相应的方法中处理产生的异常，但是这个时间非常的短，之后应用就会退出，具体多长时间我们也不清楚，很被动。如果我们可以在应用崩溃时，有足够的时间收集并且上传到服务器，那么给我们的分析和解决BUG会带来相当大的便利。  

下面直接上代码，非常简单：  

```ObjC
    CFRunLoopRef runLoop = CFRunLoopGetCurrent();
    CFArrayRef allModes = CFRunLoopCopyAllModes(runLoop);
    while (!isQuit){
        for (NSString *mode in (__bridge NSArray *)allModes) {
            CFRunLoopRunInMode((CFStringRef)mode, 0.001, false);
        }
    }
    CFRelease(allModes);
```

把上面的代码添加到 Exception 的handle方法中，此时创建了一个 RunLoop ，让这个 RunLoop 在所有的 Mode 下面一直不停的跑，保证主线程不会退出，我们的应用也就存活下来了。

参考：  
[https://developer.apple.com/reference/corefoundation/cfrunloopref](https://developer.apple.com/reference/corefoundation/cfrunloopref)  
[http://iphil.cc/?p=279](http://iphil.cc/?p=279)  
[http://blog.ibireme.com/2015/11/12/smooth_user_interfaces_for_ios/](http://blog.ibireme.com/2015/11/12/smooth_user_interfaces_for_ios/)
[http://www.itdadao.com/article/25145/](http://www.itdadao.com/article/25145/)  

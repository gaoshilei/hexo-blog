---
title: Weex从入门到超神（二）  
date: 2017-09-26 18:10:21  
categories:  
- 技术笔记  
tags:  
- Weex  
- Vue  
- JS  
- 前端  
permalink: weex-2  

---
# Weex从入门到超神（二）

## 前言  
距离我写的上一篇文章 [Weex从入门到超神（一）](https://gaoshilei.com/2017/05/26/weex-1/) 已经过了挺久了（惭愧而不失礼貌的微笑），起初写那篇文章的初衷是因为项目中使用到了 Weex ,所以准备对 Weex 做一个心得式的笔记，后来无意间发现[简书“霜神”](http://www.jianshu.com/u/12201cdd5d7a)已经对 Weex 写过几篇剖析比较深刻的文章，还有其他一些原因（懒），所以就没有继续写下去。  
最近由于Facebook的 [BSD license](https://github.com/facebook/react/blob/master/LICENSE)，React 被前端社区的同学们推到了风口浪尖，React&RN、Vue&Weex 又成为了大家码前码后讨论的话题。Apache 社区还因为 Facebook 的 BSD license，全面封杀使用了 BSD license 的开源项目，貌似一切都很精彩，迫于前端同(da)学(lao)的淫威还有社区的强烈谴责，上周 Facebook 终于认怂了，承诺这周将 React 以及 gayhub 上面的其他几个项目的开源协议从 BSD 改成 MIT，下图是我脑补的场景：  
![](http://oeat6c2zg.bkt.clouddn.com/FA269E01D9C3794449AA6748EA6280C6.png)  
鉴于对于项目中使用 Weex 的一些经验和心得，还是希望写出来和大家一起分享。  

## 应用层核心组件
Weex 运行时会先注入一段位于 `pre-build` 下的 `native-bundle-main.js` 代码。不过在注入这段代码之前会先注册一些默认的 `Component`、`Module`和`Handler`，**这就是 Weex 与 Native 应用层交互最核心的部分**，可以理解为“组件”。其中 Component 是为了映射 Html 的一些标签，Module 中是提供一些 Native 的一些方法供 Weex 调用，Handler 是一些协议的实现。  

![](http://oeat6c2zg.bkt.clouddn.com/weex-component.png)  

注册完 Weex 默认的“组件” 之后，注入刚才那段 JS，这个时候 Vue 的标签和动作才能被 Weex 所识别和转换。  
**为了便于下文的描述和理解，我把 Native 这边的 SDK 称作 Weex，前端的 Vue 和 Weex 库以及 Vue 编译后的 js 统称为 Vue**

### 1. 组件：Component
目前 Weex 一共提供了26种 Component，比较常见的有 `div`、`image`、`scroller`... ，有些跟 html 标签重名，有些是 Weex 自定义的。Weex 注册的 Component 有两种类型，一类是有`{@"append":@"tree"}`属性的标签，另一类是没有`{@"append":@"tree"}`属性的标签。要搞清楚这两类标签有什么不同，我们就要看一下 Component 的注册的源码实现。  

```Objective-C  
    [WXComponentFactory registerComponent:name withClass:clazz withPros:properties];
    NSMutableDictionary *dict = [WXComponentFactory componentMethodMapsWithName:name];
    dict[@"type"] = name;
    if (properties) {
        NSMutableDictionary *props = [properties mutableCopy];
        if ([dict[@"methods"] count]) {
            [props addEntriesFromDictionary:dict];
        }
        [[WXSDKManager bridgeMgr] registerComponents:@[props]];
    } else {
        [[WXSDKManager bridgeMgr] registerComponents:@[dict]];
    }  
```  

首先通过一个工厂类`WXComponentFactory`注册 Component，  

>  这个工厂类（单例）中管理了所有的 Component ，注册的每一个 Component 都会用一个对应的 `WXComponentConfig`来保存标签name、对应的class和属性，最后由`WXComponentFactory`来统一管理这些`WXComponentConfig `   

这一步同时注册了 Component 中的 methods，关于 method 也有两类，一类是包含`wx_export_method_sync_`前缀的同步方法，另一类是包含`wx_export_method_`前缀的异步方法（*这两种方法有什么不同，后面会有介绍*）。在`WXComponentConfig`的父类`WXInvocationConfig`储存了 Component 的方法map:  

```  
@property (nonatomic, strong) NSMutableDictionary *asyncMethods;
@property (nonatomic, strong) NSMutableDictionary *syncMethods;
```  

然后再从`WXComponentFactory`拿到对应 Component 的方法列表字典，需要注意的是这里拿到的方法列表只是**异步方法**，得到的是这样的字典：  

```  
{
    methods =     (
        resetLoadmore
    );
    type = scroller;
} 
```

不过大部分 Component 并没有`wx_export`前缀的 method，所以很多这里拿到的方法都为空。  
最后也是最关键的一步，要将 Component 注册到`WXBridgeContext`中。  

```  
    if (self.frameworkLoadFinished) {
        [self.jsBridge callJSMethod:method args:args];
    } else {
        [_methodQueue addObject:@{@"method":method, @"args":args}];
    }  
```  

最后将 Component 注册到了`JSContext`中，

>  还记得文章开头介绍的`native-bundle-main.js`吗？这里的注册调用了js中的`registerComponents`方法，这个 Component 与 Vue 就联系起来了，在 Vue 就可以使用这个 Component。
 
并且从上面的这段代码可以看出来，Component 的注册操作是在 JSFramework 加载完成才会进行，如果`native-bundle-main.js`没有加载完成，所有的 Component 的方法注册操作都会被加到队列中等待。其中的第二个参数`args`就是上面我们拿到的字典。不过有属性的 和没属性的有点区别，有属性的会将属性添加到之前拿到的字典中作为`args`再去注册。  
要搞清楚这个属性干嘛的，我们先看一下`WXComponentManager`中的相关源码： 

```  
- (void)_recursivelyAddComponent:(NSDictionary *)componentData toSupercomponent:(WXComponent *)supercomponent atIndex:(NSInteger)index appendingInTree:(BOOL)appendingInTree {
		...    
	BOOL appendTree = !appendingInTree && [component.attributes[@"append"] isEqualToString:@"tree"];
    // if ancestor is appending tree, child should not be laid out again even it is appending tree.
    for(NSDictionary *subcomponentData in subcomponentsData){
        [self _recursivelyAddComponent:subcomponentData toSupercomponent:component atIndex:-1 appendingInTree:appendTree || appendingInTree];
    }
    if (appendTree) {
        // If appending tree，force layout in case of too much tasks piling up in syncQueue
        [self _layoutAndSyncUI];
    }
}
```  

这个方法是 Vue 页面渲染时所调用的方法，这个方法会递归添加 Component，同时会向视图中添加与 Component 相对应的 UIView。从代码的后半部分可以看到，如果当前 Component 有`{@"append":@"tree"}`属性并且它的父 Component 没有这个属性将会强制对页面进行重新布局。可以看到这样做是为了防止UI绘制任务太多堆积在一起影响同步队列任务的执行。    

搞清楚了 Component 的注册机制，下面重点扒一下 Component 的运行原理：Vue 标签是如何加载以及渲染到视图上的。  
从刚才的注册过程中发现，最后一步是通过`_jsBridge`调用`callJSMethod`这个方法来注册的，而且从`WXBridgeContext`中可以看到，这个`_jsBridge`就是`WXJSCoreBridge`的实例。`WXJSCoreBridge`可以认为是 Weex 与 Vue 进行通信的最底层的部分。在调用`callJSMethod`方法之前，`_jsBridge`向 JavaScriptCore 中注册了很多全局 function，因为`jsBridge`是懒加载的，所以这些操作只会执行一次，具体请看精简后的源码：  

```  
    [_jsBridge registerCallNative:^NSInteger(NSString *instance, NSArray *tasks, NSString *callback) {	
		...    
	 }];
    [_jsBridge registerCallAddElement:^NSInteger(NSString *instanceId, NSString *parentRef, NSDictionary *elementData, NSInteger index) {
		...
    }];
    
    [_jsBridge registerCallCreateBody:^NSInteger(NSString *instanceId, NSDictionary *bodyData) {
		...
    }];
    
    [_jsBridge registerCallRemoveElement:^NSInteger(NSString *instanceId, NSString *ref) {
		...
    }];
    
    [_jsBridge registerCallMoveElement:^NSInteger(NSString *instanceId,NSString *ref,NSString *parentRef,NSInteger index) {
		...
    }];
    
    [_jsBridge registerCallUpdateAttrs:^NSInteger(NSString *instanceId,NSString *ref,NSDictionary *attrsData) {
		...
    }];
    
    [_jsBridge registerCallUpdateStyle:^NSInteger(NSString *instanceId,NSString *ref,NSDictionary *stylesData) {
		...
    }];
    
    [_jsBridge registerCallAddEvent:^NSInteger(NSString *instanceId,NSString *ref,NSString *event) {
		...
    }];
    
    [_jsBridge registerCallRemoveEvent:^NSInteger(NSString *instanceId,NSString *ref,NSString *event) {
		...
    }];
    
    [_jsBridge registerCallCreateFinish:^NSInteger(NSString *instanceId) {
    	...
    }];
    
    [_jsBridge registerCallNativeModule:^NSInvocation*(NSString *instanceId, NSString *moduleName, NSString *methodName, NSArray *arguments, NSDictionary *options) {
		...
    }];
    
    [_jsBridge registerCallNativeComponent:^void(NSString *instanceId, NSString *componentRef, NSString *methodName, NSArray *args, NSDictionary *options) {
		...
    }];

```

从这些方法名看，大多数都是一些与 Dom 更新相关的方法，我们在`WXJSCoreBridge`中更细致的看一下是怎么实现的：  

```  
- (void)registerCallAddElement:(WXJSCallAddElement)callAddElement
{
    id callAddElementBlock = ^(JSValue *instanceId, JSValue *ref, JSValue *element, JSValue *index, JSValue *ifCallback) {
        
        NSString *instanceIdString = [instanceId toString];
        NSDictionary *componentData = [element toDictionary];
        NSString *parentRef = [ref toString];
        NSInteger insertIndex = [[index toNumber] integerValue];
        [WXTracingManager startTracingWithInstanceId:instanceIdString ref:componentData[@"ref"] className:nil name:WXTJSCall phase:WXTracingBegin functionName:@"addElement" options:nil];
         WXLogDebug(@"callAddElement...%@, %@, %@, %ld", instanceIdString, parentRef, componentData, (long)insertIndex);
        
        return [JSValue valueWithInt32:(int32_t)callAddElement(instanceIdString, parentRef, componentData, insertIndex) inContext:[JSContext currentContext]];
    };

    _jsContext[@"callAddElement"] = callAddElementBlock;
}
```  

这是一个更新 Dom 添加 UIView 的方法，这里需要把 Native 的方法暴露给 JS 调用。但是有一个问题：  
>  OC 的方法参数格式和 JS 的不一样，不能直接提供给 JS 调用。  

所以这里用了两个 Block 嵌套的方式，在 JS 中调用方法时会先 invoke 里层的 callAddElementBlock，这层 Block 将 JS 传进来的参数转换成 OC 的参数格式，再执行 callAddElement 并返回一个 JSValue 给 JS，callAddElement Block中是在`WXComponentManager`中完成的关于 Component 的一些操作，这在上面介绍 Component 包含 `tree`属性问题时已经介绍过了。  
至此，简单来说就是：Weex 的页面渲染是通过先向 JSCore 注入方法，Vue 加载完成就可以调用这些方法并传入相应的参数完成 Component 的渲染和视图的更新。  
要注意，每一个 `WXSDKInstance` 对应一个 Vue 页面，Vue 加载之前就会创建对应的 WXSDKInstance，所有的 Component 都继承自`WXComponent`，他们的初始化方法都是  

```
-(instancetype)initWithRef:(NSString *)ref
                      type:(NSString *)type
                    styles:(NSDictionary *)styles
                attributes:(NSDictionary *)attributes
                    events:(NSArray *)events
              weexInstance:(WXSDKInstance *)weexInstance  
```  

这个方法会在 JS 调用`callCreateBody`时被 invoke。 

### 2. 组件：Module  
Module 注册流程和 Component 基本一致，首先通过`WXModuleFactory`注册 Module  

``` 
- (NSString *)_registerModule:(NSString *)name withClass:(Class)clazz
{
    WXAssert(name && clazz, @"Fail to register the module, please check if the parameters are correct ！");
    
    [_moduleLock lock];
    //allow to register module with the same name;
    WXModuleConfig *config = [[WXModuleConfig alloc] init];
    config.name = name;
    config.clazz = NSStringFromClass(clazz);
    [config registerMethods];
    [_moduleMap setValue:config forKey:name];
    [_moduleLock unlock];
    
    return name;
}
```  

注册 Moudle 的`registerMethods`方法与注册 Component 是一样的，都是`WXInvocationConfig`中的实例方法，`wx_export_method_sync_`前缀的同步方法注册到 syncMethods 中，`wx_export_method_`前缀的异步方法注册到 asyncMethods 中。再将 Moudle 的同步和异步方法取出来注入到`JSContext`中  

```
{
    dom =     (
        addEventListener,
        removeAllEventListeners,
        addEvent,
        removeElement,
        getComponentRect,
        updateFinish,
        scrollToElement,
        addRule,
        updateAttrs,
        addElement,
        createFinish,
        createBody,
        updateStyle,
        removeEvent,
        refreshFinish,
        moveElement
    );
}
```  

这是`WXDomModule`中所有的方法，*Moudle 中方法注册比 Component 更有意义，因为 Moudle 中基本上都是暴露给 Vue 调用的 Native 方法。*   
接下来我们来看一下 syncMethods 和 asyncMethods 有什么不同：  

 





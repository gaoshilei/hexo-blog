## debugserver动态调试
###  **在iOS上用debugserver来attach进程**
> debugserver *:1234 -a "SpringBoard"

### **在OSX上用lldb远程调试**

#### 首先在Terminal中运行lldb，然后输入以下命令：
> process connect connect://iOSIP:1234

### **获取ASLR的offset**
> image list -o -f

### **在内存地址上下断点**
> br s -a 0xb446+0x9a000

或
> br s -a 0xA5446

### **还可以通过`br dis`、`br en`和`br del`系列命令来禁用、启用和删除断点。如果要禁用所有断点（`dis`代表`disable`)**
#### 启用某个断点
> (lldb) br en 6

#### 禁用某个断点  
> (lldb) br dis 6

#### 启用所有断点（“en”代表“enable”）的命令如下：
> (lldb) br en  
> All breakpoints enabled. (2 breakpoints)  

#### 删除所有断点（“del”代表“delete”）的命令如下：  
> (lldb) br del

#### 删除某个断点  
> (lldb) br del 8

#### 指定在某个断点得到触发的时候，执行预先设置的指令，它的用法如下:
**(假设1号断点位于某个objc_msgSend函数上)**
> (lldb) br com add 1  
Enter your debugger command(s). Type 'DONE' to end.  po [$r0 class]  p (char *)$r1  c  DONE  

**这里输入了3条指令，1号断点一旦触发，就会顺序执行它们，如下：**
> (lldb) c   Process 97048 resuming   __NSArrayM  (char *) $11 = 0x26c6bbc3 "count"  Process 97048 resuming  Command #3 'c' continued the target.  




---
title: "记Raspico的开发过程"
date: 2021-11-07T18:00:27+08:00
draft: true
---

# 前置背景

Raspberry Pi 4b不多说了，我另外还有个Raspberry Pico，也是树莓派基金会发布的一个微控制器开发板。其中芯片是树莓派基金会自研的RP 2040，可以拿来做控制。

Pico官方给了microPython和C/C++的SDK，一般来说前者对底层硬件的封装更为完备，而后者就暴露了更多的硬件属性，更适合用来做一些高性能开发，我目前偏向于后者。

![l_bmepico01](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652621677279_2482.png&versionDescriptor[versionOptions]=0&versionDescriptor[versionType]=0&versionDescriptor[version]=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

供电上，Pico可以USB接口供电，亦可通过5v针脚供电。另外，它也引出了为数不少的支持各类通信协议的针脚。Pin 39 VSYS即可5v电压供电，另外Pin 1/2可通过串口进行程序的烧录，底部三个debug针脚可以直接开展相应的调试工作。

*串行调试（SWD）是基于Cortex-M的微控制器上的标准接口，主机可直接使用该接口重置开发板和烧录、调试程序。Pico将RP2040的SWD接口暴露在电路板底部边缘的三个引脚上。主机可以随时使用SWD端口访问RP2040内部而无需手动重置开发板或按住BOOTSEL按钮采用uf2启动模式。*

都串口了，同时又是嵌入式C/C++的开发，最好是一个Linux环境，这当然用Rpi 4b最方便了。

# 开发缘由

Pico支持两种烧录模式，一种是长按bootset按钮后将它插入电脑USB接口中再把编译好的uf2文件拖入到系统挂载的大容量存储设备中，一种是串口用OpenOCD直接命令烧录。前者更适合小白，但是在debug或者其他一些需要频繁烧录的时候就让人恶心透顶，你要不断的插拔USB线，过程中还要按着BOOTSET按钮；后者相对来说就更方便了，敲敲键盘就好，不必要频繁动手去做一些物理操作，不过总体的配置过程就有点水平要求了。

显然后者更为优雅，我必然也是追求后者那种优雅的开发模式的，但是这东西连接串口的时候就又像其他那些老古董一样恶臭了，我表示不能接受那种乱糟糟的还要一直连着的杜邦线。

![image-1](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652621849067_8813.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)



![image-2](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652621859336_8002.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

上图展示了最终比较理想的连接效果，即Rpi 4b为Pico 5v供电，同时二者之间用串口进行程序烧录，SWD进行程序的寄存器级别调试，全流程不需要按什么按钮或者插拔什么线缆，双手可以不离开键盘完成这一切。~~这已经优雅到不像嵌入式开发了好么……~~

敏捷调用一些小模块的时候，用杜邦线去简单测试一下这当然没问题，但是串口烧录、供电和debug这种伴随全开发流程的东西居然还要一直连着那种乱七八糟的线，我干不出来这种事。

PCB什么作用？其中一个不就是搞掉这些乱糟糟的走线的么……那就画个板好了，虽然以前从未正式探索过这棵科技树。

# 开发过程

## 硬件部分

某宝找了一圈，没有我想要的那种东东，只好自己动手做，又喜闻嘉立创可以免费打板，这更坚定了我去薅羊毛的决心没钱。女朋友说立创EDA傻瓜式画PCB，那应该就很适合我这个新手，下好立创EDA，嘉立创下单助手，开始干活。一开始我并不怎么明白PCB的设计流程，就只好对着官方的操作手册边做边看，同时不断问自己「为什么要有这么一个流程？这流程是做什么的」这种问题，还好，最后几个小时就基本明白了。

### 原理图

![image-5](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622078898_8534.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

首先是原理图，原理图给出的是各个电子器件之间的逻辑联结关系，它描述了各个器件之间是怎么连接的，或者说，是表达「哪个接口和哪个接口连一起」这个问题的工具。画图的时候，我对最初的想法有了略微的改动：把Pico和Rpi 4b的引脚都引了出来，再按照上述要求把相应的针脚连接到一起，我又额外在Rpi 4b的5v引脚上引出了一对给风扇供电的引脚。这里还有个问题，就是说怎么确定每个模块的封装，我一开始也根本找不到排母和排针在哪儿，怎么办？多试试，反正选错了女朋友也不会分手，大不了删档重开，谁让你是新手，低效率解决问题是应该的（

### PCB

#### 布局与层次关系

![image-6](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622103248_4161.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

其次是PCB，这个过程中有一个「原理图转PCB」的步骤，图中也明显体现了各个模块之间的逻辑联结关系，这个联结关系即由刚刚的原理图给出。值得说明的是，PCB又分为各种层，名字上叫得天花乱坠让人直呼真看不懂，可简单一想就能理解为什么要这么做了：Photoshop里建立了电子图片中「图层」的概念，即将不同的元素视作不同的图层，每层之间相互独立又互相耦合——独立编辑，耦合呈像。PCB中「层」的概念，我的理解和「图层」类似，即把打印字符、实际布线等等分开考虑，类似于一种「元素组」。至于说多层板，我目前涉及不多，对其理解还简单停留在「有多层布线，之间用过孔连接」的程度。其实简单一想，电源也好信号也罢，之间必然会因为电磁效应而互相影响，高速通信（频率高）时这种影响会更强，导致电路系统不能正常工作也完全是有可能的。这还没涉及到更微观的芯片层面上的考虑，想必到那一步必然会有更多的门道在里面，问题总会有些解决方法的。专业工程师的专业体现在哪儿？不就体现在这儿吗……Pico官方文档上不用针脚供电而用USB供电，我觉得可能也有信号干扰等等这些方面的考虑，只是我现在的知识水平或许还达不到那个层次，而且我也不用Pico去做一些特别高大上的东西，针脚就先用着吧，出了问题以后就再更新个Raspico的版本号（逃

#### 布线

![image-9](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622128820_5394.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

把相应的元素在PCB上摆放完毕之后，就可以进行布线了——用具体的走线把原有的逻辑关系给落地成实际的导线电路。

##### 小插曲

布线可以手动布也可以自动布，我当然要先试试自动布线，立创EDA自动布线有云端和离线两种方式，实际下下来发现这玩意儿也就是用Java跑了个本地服务，可能立创EDA再去调相应的接口。当时我身边有个计科的朋友在，我随口问他一句这玩意儿实质上是不是就是个图形学上的路径规划问题，他说是。嗯，或许以后有时间可以研究一下。

![image-7](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622160055_5553.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

这里还有个小插曲，我运行的时候本地服务器这货给我报错端口已占用，这更确定了它是个本地服务了，简单看了下它的目录结构，我想扒出来它配置文件然后看看它究竟用了哪个端口，如上图所示，这肯定要打开config文件夹了，打开发现里面又有个local，这和刚刚确定的本地服务器又对应起来了，再进去，main.json人比花娇地就在那儿趴着呢。

![image-8](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622184139_2660.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

打开，标准的配置文件格式，用了3579端口。cports走一波，发现没有被占用。这就有点懵，同时联想到我Clash偶尔会开机端口被强制置0，重启之后恢复正常，感觉这事没这么简单，直接就用了云端布线。这事一直也就搁下了，最近几天我Jetbrains全系IDE也全部GG，又促使我去搞定了这个问题，未来更新记录一下这个搞事的过程。

自动布线完毕之后，十分有必要去亲自检查一下它人工智障有没有给你干坏事强行给嘉立创创收，发现还真有，傻逼居然把过孔放在了排母底下……虽然我没经验但我不傻啊，你这么搞我我还是能看明白的，行吧我手工再微调一下，感觉比较可以，布线完毕！

![image-10](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622210019_7412.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

#### 覆铜

然后就是覆铜，覆铜这个一开始我确实是没怎么搞明白，后来简单查了一下，有些明白了。覆铜我的理解，它就是把一些引脚给连接上大面积的铜箔，然后这个铜箔基本覆盖在整个电路板上——为什么是基本？因为你不能跨过其他走线。这样一来，自然覆铜范围内的电位就和该引脚时刻保持一致了。作用？大概就是可以屏蔽掉一些无关的电磁干扰之类的吧，这个我不太明白，而且我觉得我这么简单的东西覆不覆说实话对性能来说应该是无所谓的，但是这是追求，你放一片铜上去它不结实点吗，是吧？虽然大概率没啥用，但这是追求。我决定是给GND覆铜，选中GND管脚，覆上，感觉还有点好看。

最后加上一些相应管脚的标注，放些相关的注释信息，就搞定了。以下是渲染图：

![Snipaste_2021-11-07_14-27-12](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622273029_4155.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

![Snipaste_2021-11-07_14-27-35](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622283505_7813.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

![image-12](https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622326652_9890.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0)

## 软件部分

硬件有了，软件也要相应配合。回归初心，我做这个玩意儿的目的就是要优雅的使用OpenOCD和gdb进行烧录和debug，具体配置过程确实挺简单的，不放shell命令记录了，简单说下流程。具体的细节在官方文档中也都有。

首先下好SDK，配环境变量告诉系统你这玩意儿在哪儿，之后就可以去下OpenOCD了，记得装那一堆必须要用的工具链。OpenOCD下好，初始化编译一下，就可以拿来用了。直接怼命令就好了，一堆参数记得加上，一般就是一些板子的配置文件和elf文件的路径啥的比较重要，最后也别忘了verify reset exit，不然可能你引导会出问题。

哦这里编译的时候用到了CMake，这玩意儿基本是C/C++大型项目必备，有时间可以简单再更新一些教程之类的，这里就先不说了。

OpenOCD命令可以直接地、反复地烧录，你全程不必要去碰开发板，只需要在shell里敲些命令就好了。

接下来是gdb，这货也经典至极了，配合一些人类使用现代化的IDE或者强大如VSCode的编辑器可以十分优雅的debug，也不多说了，网上教程一大堆，同时各类资料也超级丰富，树莓派基金会官方也提供了Pico的launch.json和setting.json。再强调一遍，这里的软件部分所有内容在官方文档中都有具体细节，只不过文档是全英文的 ;-P

搞定这些之后，就可以用Rpi 4b中的VSCode去十分优雅的开发了（写完代码鼠标点一下按钮就可编译，且编译可选debug、release等等不同模式，编译完毕之后在内置shell中几个命令就可以烧录过去），一般也没啥人去直接插键鼠显示器给Rpi 4b用，大家都远程居多，但是远程就不可避免的带来一个性能问题，而性能问题又是一个工程师不能妥协的问题，所以必须要用笔记本上的IDE或者VSCode开发才行，怎么办？用一些VSCode remote插件就好了，相当于用ssh去连接，性能上没任何问题，但是配置上有问题。可能是CMake配置上出了些什么错，我目前在本地win11上调用不了远程的VSCode CMake插件，所以只能写写代码，编译的话要用shell命令，烧录自然也是，而且debug体验基本没有，这些虽然都能够在Rpi远程上补足，但是我不想这么做。

以后解决掉这个问题再在这里更新一次好了，那个时候可能我的水平又更上一层楼了 ;-P

# 全家福

<img src="https://dev.azure.com/GhZhang/7555adf3-d88c-428a-b674-9622fd633f8b/_apis/git/repositories/b4894a8f-1d8d-43ad-84aa-d5ec8748e71b/items?path=%2F1652622379264_1842.png&versionDescriptor%5BversionOptions%5D=0&versionDescriptor%5BversionType%5D=0&versionDescriptor%5Bversion%5D=master&resolveLfs=true&%24format=octetStream&api-version=5.0" alt="IMG_20211107_150141" style="zoom:50%;" />

我本来还有个Rpi第三方外壳，配合有风扇，我把风扇从里面掏出来，放到侧面来散热。注意过程中一些比如Rpi GPIO接口之类数据的测量和布局，所谓机电不分家嘛，何况电又有硬件和软件呢。

# 重要说明

GitHub rep地址：https://github.com/wolfyzhang-github/Raspico

禁止任何C语言考90+但不知道gcc为何物的人士提问！我C语言考70分的人解答不了你们的问题！十分抱歉！请多包涵！

# 禅定时刻

今天初冬大雪，昨晚英雄联盟全球总决赛，男生疯狂完了女生欢呼，写作过程中楼下莺歌燕舞连绵不绝，现在我写完了，只有大妈铲雪的声音。雪人堆完终归要铲掉，谁来铲？谁想铲？

这篇文章写了四个小时，小米手环提醒我好几次久坐，我可是一个追求生活质量的人呐。下楼，运动，喝水，用膳！

---
title: 浅析Android的Recovery和Fastboot
date: 2022-07-29 23:19:58
updated: 2022-07-30 23:19:58
pinned: true
id: analysis-of-Android's-Recovery-and-Fastboot
---

Recovery应该类似于PE系统，是一个简单但是完整的Linux，有文件系统和简单的UI，可单独引导。从硬盘分区上来看，Recovery也是和内核所在的分区隔离开的，除非用户主动进行一些修改的操作，否则内核分区没办法对Recovery分区造成影响，从而侧面达成了「当内核出问题时进Recovery进行修复」的目的。

Recovery本身功能并不复杂，但是架不住这么多技术狂热分子折腾，结果就形成了一方面twrp等第三方Recovery功能强大到飞起另一方面厂商原版Recovery功能极其简陋（甚至不包括Recovery设计之初的恢复系统内核的功能）。用Recovery进行系统修复时，显然我们只需要把镜像或者Google Update格式的升级包放在手机本地存储上然后让本身就是完整OS的Recovery去读取、写入即可，就完成了内核的修复或者更新等工作。

Fastboot本身应该不是一个完整的操作系统，我更倾向于它是一个工具，一种BootLoader的软件模式，作为BootLoader的一部分而存在，使得BootLoader可以和PC进行基于USB串口的数据通信。这也能够解释为什么Fastboot模式必须要用数据线和PC连接而不能像Recovery一样读取手机本地存储内容了。

另外一个角度，我觉得它和某些使用uboot作为BootLoader的开发板上的「连接下载器时短接xx引脚」是一样的东西。现在厂商们基本都给新产品加了BL锁，而解锁就相当于去掉Fastboot指令里的校验模块。

在网上看到另一种观点把Fastboot和BootLoader作为同一事物的不同名称，考虑到有平时口语不严谨的问题，我去Android官方文档上看了一下，找到了如下字句：「You can flash a device when it's in the `fastboot` bootloader mode. To enter `fastboot` mode when a device is undergoing a cold boot, use the key combinations given in the table below」，我试着翻译一下：你可以在设备处于`fastboot` bootLoader模式下进行刷写操作。当设备处于冷启动状态时，要进入`fastboot`模式，请使用下表中的组合键。所以我最终对Fastboot的理解还是「Android设备BootLoader的一种特殊模式」和「使得BootLoader可以和PC进行串口间通信的一种工具」。

BootLoader的功能就很稀松平常了，无非就是boot负责设备硬件初始化（CPU Clock和Register之类）,Loader负责系统（Recovery或Android）的引导。


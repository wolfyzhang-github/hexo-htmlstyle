---
title: 基于YEMU思路的Y86-64指令集仿真器
date: 2022-08-24 11:09:14
updated: 2022-08-24 11:09:14
twitter:
draft:
pinned: true
---

书接上回，在上次决定要[「抖擞一下精神」](https://wolfyzhang-github.github.io/2022/08/16/%E5%AF%B9Chisel%E6%B5%85%E5%B0%9D%E8%BE%84%E6%AD%A2%E5%90%8E%E7%9A%84%E6%83%B3%E6%B3%95/)后，现在终于可以小小展示一下成果了：

首先放上源码：https://github.com/wolfyzhang-github/Brat

![shot](images/shot_1.png)

可以看到一个简单的「流水账」指令执行模拟程序，从传入的ASCII编码的二进制文件中读取位级指令，然后依次执行fetch、decode、execute、read memory、write memory和update pc等流程，一套流程走完了，这一条指令也就执行完了。出于在时间安排上的考虑，我选了CSAPP 3e中为教学设计的Y86-64指令集，它足够简单，同时一些常用的指令元素也基本都有涉及，关于Y86-64的具体内容这里就不再多言。

说起来，我本来是想用HDL实现一个CPU，但是最后花在toolchains上的时间却远大于CPU本身，其完成度也更高。与配套的工具链相比，CPU本身倒像是一个副产品，所以，干脆本文也以toolchains作主要分析对象了。下面，我简要介绍一下我做的这个微小工作。

Toolchains包括如下内容，其中yie是最主要的：

- yie：y86-84 isa emulator

- assembler：用于将官方汇编器汇编后的汇编程序文本转换为二进制文本的Python脚本

- sum：演示 yie 功能的样例程序

- test：yie的部分测试用例

sum是一个数组求和程序，其等效的C程序如下：

```C
long sum(long *arr, long count) {
    long sum = 0;
    while (count) {
        sum += *arr;
        arr++;
        count--;
    }
    return sum;
}
```

由于没有y86-64版本的C语言编译器，所以我们必须手工编写对应的汇编代码，`sum.ys`内容节选如下：

```assembly
# Execution begins at address 0
    .pos 0
    irmovq stack, %rsp  # Set stack pointer
    call main
    halt
# Array of 4 elements
    .align 8
array:
    ......

main:
    irmovq array, %rdi
    irmovq $4, %rsi
    call sum             # sum(array, 4)
    ret
# long sum(long *start, long count)
# start in %rdi, count in %rsi
sum:
    ......

    jmp test        # Goto test
loop:
    mrmovq (%rdi), %r10 # Get *start
    addq %r10, %rax     # add to sum
    addq %r8, %rdi      # start++
    subq %r9, %rsi      # count--, set CC
test:
    jne loop           # Loop if count != 0, stop when 0
    ret                # Return sum
# Stack starts here and grows to lower addresses
    .pos 0x100
stack:
```

然后我们就可以通过isa手册将上面代码进行手工汇编，将其转译成计算机可以实际运行的二进制文件`sum`。CSAPP官方提供了一个汇编器用于产生汇编代码和二进制代码一一对应的程序文本。值得指出，官方汇编器实际上是把一个ASCII码编码的文件进行处理，然后输出另一个ASCII码编码的文件，而ASCII码编码过的文本文件是不能够直接被计算机执行的（即便其内容是二进制程序），其机内码和我们可以阅读的数字不一致，我们必须再对「ASCII码编码过的二进制程序文本文件」进行处理，使用HexEditor等工具，直接写入该文件的机内码。

使用该汇编器对上面的汇编代码进行处理产生的「汇编代码和二进制代码一一对应的程序文本」`sum.yo`节选如下：

```assembly
                            | # Execution begins at address 0
0x000:                      |     .pos 0
0x000: 30f40001000000000000 |     irmovq stack, %rsp  # Set stack pointer
0x00a: 803800000000000000   |     call main
0x013: 00                   |     halt

......

0x077:                      | loop:
0x077: 50a70000000000000000 |     mrmovq (%rdi), %r10 # Get *start
0x081: 60a0                 |     addq %r10, %rax     # add to sum
0x083: 6087                 |     addq %r8, %rdi      # start++
0x085: 6196                 |     subq %r9, %rsi      # count--, set CC
0x087:                      | test:
0x087: 747700000000000000   |     jne loop           # Loop if count != 0, stop when 0
0x090: 90                   |     ret                # Return sum
                            | 
                            | # Stack starts here and grows to lower addresses
0x100:                      |     .pos 0x100
0x100:                      | stack:
                            |

```

同时，CSAPP官方又提供了另外一个模拟器，来模拟y86-64 CPU的具体行为，采用该模拟器运行上面的`sum.yo`后的结果如下：

![shot_2](images/shot_2.png)

而我做的工作，就是实现了一个将每一个操作周期都显式表示出来的y86-64仿真程序（包括测试脚本），以及一个将「汇编代码和二进制代码一一对应的程序文本」转换为纯二进制程序文本的工具。前者是yie，后者是assembler。

yie的实际实现上，因为没有流水线化的概念，所以其实所有指令都是在一个`while(1)`循环内依次进行执行的：

```C
pc = 0;
for (int i = 0; ; ++i) {
  printf("\n"TITLE"No.%d cycle:"COLOR_NONE"\n", i+1);
  fetch(memory[pc]);
  decode();
  execute();
  readMemory();
  writeMemory();
  updatePC();
  ......
    if (state) break;
}
```

具体到每个执行阶段，实际上也就是通过不同的操作码进行switch匹配，再执行对应操作。而这个实现思路，就来源于PA实验中提到的「YEMU」。

assembler则只是对官方汇编器产生的「汇编代码和二进制代码一一对应的程序文本」进行字符处理，直接输出ASCII码编码的二进制程序文本。

我实现的这套东西本身是y86-64 SEQ CPU的辅助工具，或者说是脚手架，是基础设施，而这套东西本身又有它们自己的辅助工具，比如yie的测试脚本和Makefile组成的「编译系统」等。基础设施是对整个产品生产过程中所遇到问题的一整套解决方案，它的价值不仅体现在它能解决当下的这一个具体问题，更体现在它背后所代表的那一套可以推而广之的对问题的解决机制上。

*** 

项目上暂时告一段落，今年接下来的几个月就安心准备考研。

毕设如果可以的话，希望能够依托「一生一芯」计划，设计一套自己的RISC-V计算机系统出来，那可太美好了。

> 对北京开芯院目前在做的「IC敏捷开发流程」愈发感兴趣了，也是业内的一个新方向，希望未来如果有机会可以去开芯院实习一段时间。
